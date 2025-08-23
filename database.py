import os
import psycopg2
import pandas as pd
from io import StringIO

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
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=True)
    buffer.seek(0)

    cur = conn.cursor()
    try:
        cur.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER", buffer)
        conn.commit()
    finally:
        cur.close()
        conn.close()
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432),
    )

# Fetch answer from DB if available
def get_answer_from_db(question):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT answer FROM qa_pairs WHERE question = %s", (question,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

# Insert new Q/A pair into DB
def add_qa_pair(question, answer):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO qa_pairs (question, answer) VALUES (%s, %s)",
        (question, answer)
    )
    conn.commit()
    cur.close()
    conn.close()
