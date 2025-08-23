import psycopg2
import os
import google.generativeai as genai
import numpy as np
import json
import faiss
import streamlit as st
import io

# Configure Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# ✅ Connection
def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        dbname=st.secrets["DB_NAME"]
    )


# ✅ Get Embedding
def get_embedding(text):
    r = genai.embed_content(model="models/embedding-001", content=text)
    return r["embedding"]


# ✅ Insert one QA pair
def add_qa_pair(question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    emb = json.dumps(get_embedding(question))
    cursor.execute(
        "INSERT INTO qa_pairs (question, answer, embedding) VALUES (%s, %s, %s)",
        (question, answer, emb)
    )
    conn.commit()
    cursor.close()
    conn.close()


# ✅ Bulk insert
def execute_many_insert(query, values):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.executemany(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ✅ Bulk upload via CSV
def copy_via_csv(df, table_name):
    conn = get_connection()
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    with conn.cursor() as cur:
        cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV", buffer)
    conn.commit()
    conn.close()


# ✅ Load FAISS index
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
        except:
            continue

    if not vecs:
        return None, None

    dim = vecs[0].shape[0]
    index = faiss.IndexFlatIP(dim)
    index.add(np.vstack(vecs).astype("float32"))
    return index, answers


# ✅ Answer lookup
def get_answer_from_db(question):
    index, answers = _load_index()
    if index is not None:
        qv = np.array(get_embedding(question), dtype="float32")
        n = np.linalg.norm(qv)
        if n != 0:
            qv = (qv / n).reshape(1, -1)
            scores, idxs = index.search(qv, 1)
            score = float(scores[0][0])
            pos = int(idxs[0][0])
            if score >= 0.80:
                return answers[pos]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM qa_pairs WHERE LOWER(question) LIKE LOWER(%s) LIMIT 1", ("%" + question + "%",))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


# ✅ Backfill embeddings
def backfill_embeddings(batch_size=50):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, question FROM qa_pairs WHERE embedding IS NULL OR embedding = ''")
    rows = c.fetchall()
    u = conn.cursor()
    i = 0
    for row in rows:
        emb = json.dumps(get_embedding(row[1]))
        u.execute("UPDATE qa_pairs SET embedding=%s WHERE id=%s", (emb, row[0]))
        i += 1
        if i % batch_size == 0:
            conn.commit()
    conn.commit()
    u.close()
    c.close()
    conn.close()
