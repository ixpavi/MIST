import logging
import uuid
from pathlib import Path

import streamlit as st
from better_profanity import profanity

import config
import database
import intents
import rag

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="MIST AI - SRM Assistant", page_icon="🎓", layout="wide")

THEMES = {
    "dark": {"bg": "#0b0f1a", "bg2": "#1a1f33", "card": "#151a2b", "text": "#f1f5f9",
             "muted": "#94a3b8", "border": "#2a3150", "accent": "#818cf8"},
    "light": {"bg": "#eef4fb", "bg2": "#ffffff", "card": "#ffffff", "text": "#0f172a",
              "muted": "#475569", "border": "#cbd5e1", "accent": "#4f46e5"},
}
CAMPUSES = ["Any campus", "Kattankulathur (KTR)", "Ramapuram", "Vadapalani", "Tiruchirappalli",
            "Delhi-NCR", "Baburayanpettai"]
FOCUS = ["General", "Admissions", "Academics", "Hostels", "Fees", "Placements", "Student life"]
SUGGESTIONS = ["How do I apply through SRMJEEE?", "What are SRM's NIRF and NAAC rankings?",
               "Tell me about hostels at KTR", "Which companies recruit from SRM?"]
GREETINGS = {"hi", "hello", "hey", "hii", "sup", "good morning", "good evening"}
MAX_QUERY_CHARS = 600


# ------------------------------------------------------------------ state
def init_state():
    ss = st.session_state
    ss.setdefault("theme", "dark")
    ss.setdefault("messages", [])
    ss.setdefault("pending", None)
    ss.setdefault("session_id", uuid.uuid4().hex[:12])


@st.cache_resource(show_spinner="Loading SRM knowledge base...")
def get_kb():
    chunks, source = rag.load_kb()
    rag.ensure_embeddings(chunks)
    return chunks, source


def inject_css():
    t = THEMES[st.session_state.theme]
    tokens = ";".join(f"--{k}:{v}" for k, v in t.items())
    css = (Path(__file__).parent / "assets" / "style.css").read_text(encoding="utf-8")
    st.markdown(f"<style>:root{{{tokens}}}\n{css}</style>", unsafe_allow_html=True)


# ------------------------------------------------------------------ chat logic
def reply_to(query, name, campus, focus, length):
    """Runs the MIST AI engine. Returns the engine result dict plus log_id."""
    q = query.strip()[:MAX_QUERY_CHARS]
    if profanity.contains_profanity(q):
        return {"answer": "⚠️ Please keep our conversation respectful.", "route": "rule", "sources": [],
                "grounded": False, "score": 0.0}
    chunks, _ = get_kb()
    res = rag.answer(q, st.session_state.messages[:-1], chunks, campus, focus, length, name)
    res["log_id"] = database.log_chat(st.session_state.session_id, q, res["answer"], campus, focus,
                                      res["grounded"], res["score"]) if database.is_configured() else None
    return res


ROUTE_LABEL = {"tool": "🧮 SRM tool (exact)", "kb+llm": "📚 SRM knowledge + language model",
               "kb": "📚 SRM knowledge base", "rule": "⚙️ built-in rule", "decline": "🎯 out of scope"}


def render_message(msg, idx):
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🎓"):
        st.markdown(msg["content"])
        if msg["role"] != "assistant":
            return
        meta = msg.get("meta", {})
        if meta.get("route") in ROUTE_LABEL:
            topic = intents.LABELS.get(meta.get("intent"), "")
            conf = f" {meta['intent_conf']:.0%}" if meta.get("intent_conf") else ""
            st.markdown(f"<span class='mist-badge'>{ROUTE_LABEL[meta['route']]}</span>"
                        + (f"<span class='mist-badge'>topic: {topic}{conf}</span>" if topic else ""),
                        unsafe_allow_html=True)
        if meta.get("sources"):
            links = " · ".join(f"<a href='{s}' target='_blank'>{s.replace('https://', '').rstrip('/')}</a>"
                               for s in meta["sources"][:3])
            st.markdown(f"<div class='mist-src'>Sources: {links}</div>", unsafe_allow_html=True)
        if meta.get("log_id"):
            c1, c2, _ = st.columns([1, 1, 8])
            if c1.button("👍", key=f"up{idx}", help="Helpful"):
                database.save_feedback(meta["log_id"], 1)
                st.toast("Thanks for the feedback!")
            if c2.button("👎", key=f"down{idx}", help="Not helpful"):
                database.save_feedback(meta["log_id"], -1)
                st.toast("Thanks - this helps improve MIST AI.")


# ------------------------------------------------------------------ sidebar
def sidebar():
    with st.sidebar:
        st.markdown("## 🎓 MIST AI")
        st.caption("SRM virtual assistant")
        dark = st.toggle("🌙 Dark mode", value=st.session_state.theme == "dark")
        if dark != (st.session_state.theme == "dark"):
            st.session_state.theme = "dark" if dark else "light"
            st.rerun()

        st.markdown("### 👤 Profile")
        name = st.text_input("Your name", key="username", placeholder="Optional")
        campus = st.selectbox("Campus", CAMPUSES, key="campus")
        focus = st.selectbox("Focus area", FOCUS, key="focus")
        length = st.select_slider("Answer length", ["Short", "Medium", "Long"], value="Medium", key="length")

        st.markdown("### ⚡ Actions")
        c1, c2 = st.columns(2)
        if c1.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        msgs = st.session_state.messages
        text = "\n\n".join(f"{'You' if m['role'] == 'user' else 'MIST AI'}: {m['content']}" for m in msgs)
        c2.download_button("💾 Export", text or "No messages yet.", "mist_chat.txt", use_container_width=True,
                           disabled=not msgs)

        _, kb_src = get_kb()
        with st.expander("ℹ️ System status"):
            llm_ok = bool(config.get("GEMINI_API_KEY"))
            st.markdown(f"- SRM knowledge base: **{len(get_kb()[0])} entries** (from {kb_src})\n"
                        f"- Intent model: {'✅ trained, 15 SRM intents' if intents.load() else '⚠️ not trained'}\n"
                        "- Exact tools: ✅ SRMJEEE deadlines, programme fees\n"
                        f"- Language layer: {'✅ online' if llm_ok else '⚠️ offline (showing KB text)'}\n"
                        f"- Database: {'✅ Supabase' if database.is_configured() else '⚠️ not configured'}")
        with st.expander("🔗 Official links"):
            st.markdown("- [SRM website](https://www.srmist.edu.in)\n"
                        "- [Admissions](https://www.srmist.edu.in/admission-india/)\n"
                        "- [Hostels](https://www.srmist.edu.in/srm-hostels/)\n"
                        "- [Career Centre](https://www.srmist.edu.in/career-centre/)")
        st.caption("Unofficial student project. Verify fees and dates on srmist.edu.in.")
    return name, campus, focus, length


# ------------------------------------------------------------------ page
def main():
    init_state()
    profanity.load_censor_words()
    inject_css()
    name, campus, focus, length = sidebar()

    st.markdown("<h1 class='mist-title'>MIST AI</h1><div class='mist-sub'>Your SRM virtual assistant"
                + (f" - hi {name}! 👋" if name else "") + "</div>", unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("##### 💡 Try asking")
        cols = st.columns(len(SUGGESTIONS))
        for i, (col, s) in enumerate(zip(cols, SUGGESTIONS)):
            if col.button(s, key=f"s{i}", use_container_width=True):
                st.session_state.pending = s
                st.rerun()

    query = st.chat_input("Ask about SRM admissions, hostels, placements...") or st.session_state.pending
    st.session_state.pending = None
    if query:
        st.session_state.messages.append({"role": "user", "content": query[:MAX_QUERY_CHARS]})
        with st.spinner("Thinking..."):
            res = reply_to(query, name, campus, focus, length)
        st.session_state.messages.append({"role": "assistant", "content": res["answer"], "meta": res})

    for i, m in enumerate(st.session_state.messages):
        render_message(m, i)


main()
