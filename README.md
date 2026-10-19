# MIST AI - an SRM-specific assistant

MIST AI is **not a thin wrapper around a chatbot API**. It is a small pipeline of SRM-specific components; a language
model is only the last step that phrases the answer.

```
question
  -> profanity filter
  -> INTENT MODEL        TF-IDF + logistic regression trained on SRM questions (15 intents, 94.6% held-out accuracy)
  -> rules               greeting / identity / thanks / out-of-scope decline
  -> EXACT TOOLS         SRMJEEE deadline checker (knows today's date), programme & fee table lookup  (no LLM)
  -> HYBRID RETRIEVAL    embeddings + keyword scoring + intent-topic boost over 79 official-source entries
  -> wording layer       language model rewrites the retrieved facts; falls back across models, then to raw KB text
  -> answer + route badge + source links  (+ thumbs up/down -> Supabase -> promoted into the knowledge base)
```

## What is trained / built here
| Piece | Where | Notes |
|---|---|---|
| Knowledge base | `data/srm_knowledge.json`, `data/kb_official.json`, `data/programs.json` | every entry has a `source` URL on srmist.edu.in |
| Intent classifier | `intents.py`, `train_intent.py` -> `data/intent_model.joblib` | 1,250 training questions (hand-written + augmented), 56 held-out test questions |
| Exact tools | `tools.py` | deadlines and fees come from data, never generated |
| Retrieval + routing | `rag.py` | |
| Storage | Supabase Postgres (`schema.sql`) | `kb_chunks` (text + embeddings), `chat_logs` (questions, route, rating) |
| Learning loop | `ingest.py --promote`, Admin page | answers rated helpful become verified FAQ entries |
| Evaluation | `evaluate.py` | intent accuracy, retrieval hit@1/hit@3, routing checks |

## Run
```bash
pip install -r requirements.txt
cp .env.example .env            # GEMINI_API_KEY + Supabase DB_* values
python ingest.py --init         # create tables, embed the knowledge base, upload to Supabase
python train_intent.py          # (re)train the intent model
python evaluate.py              # print the metrics
streamlit run app.py
```
Without a Gemini key or a database it still runs (knowledge-base-only mode).

## Deploy (Streamlit Cloud)
Paste the `.env` values as TOML into *Settings > Secrets*. **Never commit `.env`.**
Unofficial student project: always confirm fees and dates on https://www.srmist.edu.in.
