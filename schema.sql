-- Run once in the Supabase SQL editor (or: python ingest.py --init)
create table if not exists kb_chunks (
    id         text primary key,
    topic      text not null default 'General',
    campus     text not null default 'All',
    text       text not null,
    source     text,
    embedding  jsonb,
    updated_at timestamptz not null default now()
);

create table if not exists chat_logs (
    id         bigserial primary key,
    created_at timestamptz not null default now(),
    session_id text,
    question   text not null,
    answer     text not null,
    campus     text,
    focus      text,
    grounded   boolean not null default false,
    top_score  real,
    rating     smallint            -- 1 = helpful, -1 = not helpful
);
