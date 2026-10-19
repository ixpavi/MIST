"""Admin page: teach MIST AI new facts by uploading a CSV (columns: topic, text, optional campus, source)."""
import hashlib

import pandas as pd
import streamlit as st

import config
import database
import rag

st.set_page_config(page_title="MIST AI - Admin", page_icon="🛠️", layout="wide")
st.title("🛠️ Admin: train the knowledge base")

password = config.get("ADMIN_PASSWORD")
if not password:
    st.warning("Set ADMIN_PASSWORD in your secrets/.env to enable this page.")
    st.stop()
if st.text_input("Admin password", type="password") != password:
    st.stop()

if not database.is_configured():
    st.error("Database not configured - uploads need Supabase (DB_HOST, DB_USER, DB_PASS).")
    st.stop()

with st.expander("Dashboard", expanded=True):
    try:
        s = database.get_stats()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Questions", s["total"])
        c2.metric("Answered from KB", s["grounded"])
        c3.metric("👍", s["up"])
        c4.metric("👎", s["down"])
    except Exception as e:
        st.info(f"Stats unavailable (has the schema been created? run `python ingest.py --init`): {e}")

with st.expander("Learning loop: promote answers students rated 👍", expanded=False):
    try:
        liked = database.get_liked()
        st.write(f"{len(liked)} helpful answers waiting.")
        if liked and st.button("Add them to the knowledge base"):
            import ingest
            chunks = ingest.liked_chunks()
            rag.ensure_embeddings(chunks)
            database.upsert_chunks(chunks)
            st.cache_resource.clear()
            st.success(f"Promoted {len(chunks)} answers.")
    except Exception as e:
        st.info(f"Unavailable: {e}")

uploaded = st.file_uploader("CSV with columns: topic, text, [campus], [source]", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded).fillna("")
    if not {"topic", "text"}.issubset(df.columns):
        st.error("CSV needs at least the columns: topic, text")
        st.stop()
    st.dataframe(df.head(20), use_container_width=True)
    if st.button("🚀 Embed and save"):
        chunks = [{"id": "csv-" + hashlib.sha1(r["text"].encode()).hexdigest()[:12], "topic": r["topic"],
                   "campus": r.get("campus") or "All", "text": r["text"], "source": r.get("source") or None}
                  for _, r in df.iterrows() if str(r["text"]).strip()]
        rag.ensure_embeddings(chunks)
        database.upsert_chunks(chunks)
        st.cache_resource.clear()
        st.success(f"Saved {len(chunks)} entries. The assistant will use them right away.")
