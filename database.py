import mysql.connector
import os
from dotenv import load_dotenv
import google.generativeai as genai
import numpy as np
import json
import faiss

load_dotenv()
if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "mist_ai")
    )

def get_embedding(text):
    r = genai.embed_content(model="models/embedding-001", content=text)
    return r["embedding"]

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

def _load_index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, answer, embedding FROM qa_pairs WHERE embedding IS NOT NULL AND embedding <> ''")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    vecs = []
    answers = []
    for row in rows:
        try:
            v = np.array(json.loads(row["embedding"]), dtype="float32")
            if v.ndim != 1:
                continue
            n = np.linalg.norm(v)
            if n == 0:
                continue
            vecs.append(v / n)
            answers.append(row["answer"])
        except:
            continue
    if not vecs:
        return None, None
    dim = vecs[0].shape[0]
    index = faiss.IndexFlatIP(dim)
    index.add(np.vstack(vecs).astype("float32"))
    return index, answers

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
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT answer FROM qa_pairs WHERE LOWER(question) LIKE LOWER(%s) LIMIT 1", ("%" + question + "%",))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row["answer"] if row else None

def backfill_embeddings(batch_size=50):
    conn = get_connection()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT id, question FROM qa_pairs WHERE embedding IS NULL OR embedding = ''")
    rows = c.fetchall()
    u = conn.cursor()
    i = 0
    for row in rows:
        emb = json.dumps(get_embedding(row["question"]))
        u.execute("UPDATE qa_pairs SET embedding=%s WHERE id=%s", (emb, row["id"]))
        i += 1
        if i % batch_size == 0:
            conn.commit()
    conn.commit()
    u.close()
    c.close()
    conn.close()
