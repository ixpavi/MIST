"""Supabase (Postgres) access. Callers treat any failure as 'DB unavailable' and fall back."""
import json
import logging
from pathlib import Path

import psycopg2

import config

log = logging.getLogger("mist.db")
SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def is_configured():
    return bool(config.get("DB_HOST") and config.get("DB_USER") and config.get("DB_PASS"))


def get_connection():
    return psycopg2.connect(
        host=config.get("DB_HOST"),
        port=config.get("DB_PORT", "5432"),
        user=config.get("DB_USER"),
        password=config.get("DB_PASS"),
        dbname=config.get("DB_NAME", "postgres"),
        sslmode=config.get("DB_SSLMODE", "require"),
        connect_timeout=8,
    )


def _run(sql, params=None, fetch=False):
    if not is_configured():
        raise RuntimeError("Database is not configured")
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall() if fetch else None
    finally:
        conn.close()


def init_schema():
    _run(SCHEMA_FILE.read_text(encoding="utf-8"))


def upsert_chunks(chunks):
    """chunks: dicts with id, topic, campus, text, source, embedding (list or None)."""
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            for c in chunks:
                cur.execute(
                    """insert into kb_chunks (id, topic, campus, text, source, embedding, updated_at)
                       values (%s,%s,%s,%s,%s,%s, now())
                       on conflict (id) do update set topic=excluded.topic, campus=excluded.campus,
                         text=excluded.text, source=excluded.source,
                         embedding=excluded.embedding, updated_at=now()""",
                    (c["id"], c.get("topic", "General"), c.get("campus", "All"), c["text"],
                     c.get("source"), json.dumps(c["embedding"]) if c.get("embedding") else None),
                )
    finally:
        conn.close()


def load_chunks():
    rows = _run("select id, topic, campus, text, source, embedding from kb_chunks order by id", fetch=True)
    out = []
    for id_, topic, campus, text, source, emb in rows:
        if isinstance(emb, str):
            emb = json.loads(emb)
        out.append({"id": id_, "topic": topic, "campus": campus, "text": text,
                    "source": source, "embedding": emb})
    return out


def log_chat(session_id, question, answer, campus, focus, grounded, top_score):
    """Returns the new log id, or None if logging failed (never breaks the chat)."""
    try:
        rows = _run(
            """insert into chat_logs (session_id, question, answer, campus, focus, grounded, top_score)
               values (%s,%s,%s,%s,%s,%s,%s) returning id""",
            (session_id, question, answer, campus, focus, grounded, top_score), fetch=True)
        return rows[0][0]
    except Exception as e:
        log.warning("log_chat failed: %s", e)
        return None


def save_feedback(log_id, rating):
    try:
        _run("update chat_logs set rating=%s where id=%s", (rating, log_id))
        return True
    except Exception as e:
        log.warning("save_feedback failed: %s", e)
        return False


def get_stats():
    rows = _run(
        """select count(*), count(*) filter (where grounded),
                  count(*) filter (where rating=1), count(*) filter (where rating=-1)
           from chat_logs""", fetch=True)
    total, grounded, up, down = rows[0]
    return {"total": total, "grounded": grounded, "up": up, "down": down}


def get_liked(limit=200):
    """Answers students marked helpful - candidates to promote into the knowledge base."""
    rows = _run(
        """select distinct on (lower(question)) question, answer from chat_logs
           where rating = 1 and grounded order by lower(question), created_at desc limit %s""",
        (limit,), fetch=True)
    return [{"question": q, "answer": a} for q, a in rows]
