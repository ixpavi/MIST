"""'Training' the assistant = building its knowledge base.

    python ingest.py --init     create tables in Supabase
    python ingest.py            embed data/srm_knowledge.json (+ data/qa_seed.csv) and upsert to Supabase
    python ingest.py --promote  also add answers students rated helpful (feedback loop)
    python ingest.py --local    embed/validate only, no database
"""
import argparse
import csv
import hashlib
from pathlib import Path

import database
import rag

QA_CSV = Path(__file__).with_name("data") / "qa_seed.csv"


def qa_chunks():
    if not QA_CSV.exists():
        return []
    out = []
    with QA_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            q, a = (row.get("question") or "").strip(), (row.get("answer") or "").strip()
            if q and a:
                out.append({"id": "qa-" + hashlib.sha1(q.lower().encode()).hexdigest()[:10], "topic": "FAQ",
                            "campus": "All", "text": f"Q: {q}\nA: {a}", "source": None})
    return out


def liked_chunks():
    """Close the learning loop: answers students rated helpful become verified FAQ entries."""
    out = []
    for r in database.get_liked():
        out.append({"id": "fb-" + hashlib.sha1(r["question"].lower().encode()).hexdigest()[:10], "topic": "FAQ",
                    "campus": "All", "text": f"Q: {r['question']}\nA: {r['answer']}", "source": None})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--promote", action="store_true", help="also add answers students rated helpful")
    args = ap.parse_args()

    if args.init:
        database.init_schema()
        print("Schema created.")

    chunks = rag.load_local_kb() + qa_chunks()
    if args.promote and not args.local:
        liked = liked_chunks()
        print(f"{len(liked)} student-approved answers promoted")
        chunks += liked
    rag.ensure_embeddings(chunks)
    embedded = sum(1 for c in chunks if c.get("embedding"))
    print(f"{len(chunks)} chunks, {embedded} embedded"
          + ("" if embedded == len(chunks) else "  (set a valid GEMINI_API_KEY to embed the rest)"))

    if not args.local:
        database.upsert_chunks(chunks)
        print("Upserted to Supabase.")


if __name__ == "__main__":
    main()
