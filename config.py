"""Central config: environment variables first, then Streamlit secrets."""
import os

from dotenv import load_dotenv

load_dotenv()


def get(name, default=None):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return st.secrets.get(name, default)
    except Exception:
        return default


CHAT_MODEL = get("GEMINI_CHAT_MODEL", "gemini-2.5-flash-lite")
# Tried in order; a busy or retired model falls through to the next one.
CHAT_MODELS = [CHAT_MODEL] + [m for m in ("gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-lite-latest")
                              if m != CHAT_MODEL]
EMBED_MODEL = get("GEMINI_EMBED_MODEL", "gemini-embedding-001")
EMBED_DIM = int(get("GEMINI_EMBED_DIM", "768"))
