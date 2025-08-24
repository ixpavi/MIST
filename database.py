import os
import psycopg2
import pandas as pd
from io import StringIO
import json
import numpy as np
import google.generativeai as genai
import faiss


if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text):
    """
    Generate embedding for a text using Gemini API
    """
    r = genai.embed_content(model="models/embedding-001", content=text)
    return r["embedding"]
# Create DB connection
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", 5432),
    )

# Bulk insert (INSERT mode)
def execute_many_insert(table, cols, rows):
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ", ".join(["%s"] * len(cols))
    colnames = ", ".join(cols)
    query = f"INSERT INTO {table} ({colnames}) VALUES ({placeholders})"
    cur.executemany(query, rows)
    conn.commit()
    cur.close()
    conn.close()

# Bulk copy (COPY mode)
def copy_via_csv(table, df, conn=None):
    conn = conn or get_connection()

    # 🔥 Drop "id" column if it exists in the CSV
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=True)
    buffer.seek(0)

    cur = conn.cursor()
    try:
        # Build the column list dynamically (avoid COPY into id)
        cols = ','.join(df.columns)
        sql = f"COPY {table} ({cols}) FROM STDIN WITH CSV HEADER"

        cur.copy_expert(sql, buffer)
        conn.commit()

        # 🔥 Immediately add embeddings for new rows
        backfill_embeddings()

    finally:
        cur.close()
        conn.close()

def _load_index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, answer, embedding FROM qa_pairs WHERE embedding IS NOT NULL AND embedding <> ''")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    vecs, answers = [], []
    for row in rows:
        try:
            v = np.array(json.loads(row[2]), dtype="float32")
            if v.ndim != 1:
                continue
            n = np.linalg.norm(v)
            if n == 0:
                continue
            vecs.append(v / n)
            answers.append(row[1])
        except Exception:
            continue

    if not vecs:
        return None, None

    arr = np.vstack(vecs).astype("float32")
    index = faiss.IndexFlatIP(arr.shape[1])   # inner product for cosine similarity
    index.add(arr)
    return index, answers



def get_answer_from_db(question, threshold=0.70):
    index, answers = _load_index()
    if index is not None:
        qv = np.array(get_embedding(question), dtype="float32")
        n = np.linalg.norm(qv)
        if n != 0:
            qv = (qv / n).reshape(1, -1)
            scores, idxs = index.search(qv, 1)  # top-1 result
            score = float(scores[0][0])
            pos = int(idxs[0][0])
            if score >= threshold:
                return answers[pos]

    # fallback: if no semantic match, try substring
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT answer FROM qa_pairs WHERE LOWER(question) LIKE LOWER(%s) LIMIT 1",
        ("%" + question + "%",)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None



# Insert new Q/A pair into DB
def add_qa_pair(question, answer):
    conn = get_connection()
    cur = conn.cursor()
    
    # Normalize question: remove leading/trailing spaces
    question_norm = question.strip()
    
    cur.execute(
        "INSERT INTO qa_pairs (question, answer) VALUES (%s, %s)",
        (question_norm, answer)
    )
    
    conn.commit()
    cur.close()
    conn.close()


def backfill_embeddings(batch_size=50):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, question FROM qa_pairs WHERE embedding IS NULL OR embedding = ''")
    rows = c.fetchall()
    u = conn.cursor()
    i = 0
    for row in rows:
        emb = json.dumps(get_embedding(row[1]))  # ✅ now get_embedding is defined
        u.execute("UPDATE qa_pairs SET embedding=%s WHERE id=%s", (emb, row[0]))
        i += 1
        if i % batch_size == 0:
            conn.commit()
    conn.commit()
    u.close()
    c.close()
    conn.close()
