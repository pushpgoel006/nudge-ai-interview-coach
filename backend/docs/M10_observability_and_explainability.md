# M10 — LangSmith tracing + reasoning panel (implementation brief)

> **How to use this file.** Implement it **one step at a time, in order**.
> After each step, stop and report exactly what changed, then wait to be told
> to continue. Do not implement several steps in one turn.
>
> Part A and Part B are independent of each other — either can be built
> first. Part B works with or without Part A. Part B degrades gracefully if
> the agentic RAG upgrade (Part B of `docs/M8_login_and_agentic_rag.md`) has
> not been built yet — see gotcha B.2.

---

## Tech stack this brief needs

Nothing new. `langsmith` is already in `requirements.txt` (pulled in as a
LangChain dependency, currently unused). Part B uses only `st.expander`,
already used elsewhere in this project's UI.

---

# PART A — Turn on LangSmith tracing

## A.1 What this is and why it's worth doing

Right now the only visibility into what a graph run actually did is the
`print()` statements in the terminal, and those disappear the moment the
terminal closes. LangSmith is a hosted dashboard that LangChain and LangGraph
can send full execution traces to, automatically, with no code changes to any
node — for every run you'd be able to see, after the fact, in a browser:
which nodes fired, the exact text sent to the retriever, which chunks came
back, the exact prompt sent to Groq, the reply, how long each step took, and
how many tokens were used.

This turns "I think my RAG pipeline works" into "here are real traces of it
working" — genuinely useful for debugging, and a concrete thing to show in an
interview.

## A.2 Before Claude Code starts — one manual step for the project owner

LangSmith requires a free account and an API key. **This step is not
something Claude Code can do — it needs a human to sign up.**

1. Go to https://smith.langchain.com and create a free account.
2. Create a new project (e.g. name it `interview-intelligence-platform`).
3. Generate an API key from the settings page.

Have the key ready before Step 1 below.

## A.3 Non-goals

- Building a custom evaluation harness / scoring pipeline — that is a
  separate, larger piece of work and deliberately not part of this brief.
- Adding any manual tracing calls (`@traceable`, custom spans) inside your own
  functions — LangChain and LangGraph already trace themselves automatically
  once the environment variables below are set. Do not add decorators
  anywhere; that is unnecessary for this brief's scope.

## A.4 Two gotchas to get right

### A.4.1 The tracing flag is a literal string, not a Python boolean

Environment variables are always strings. This must be the literal text
`true` (lowercase), not Python's `True`:

```
LANGCHAIN_TRACING_V2=true
```

### A.4.2 Never commit the API key

Confirm `.env` is already listed in `.gitignore` (it should be, given the
existing `GROQ_API_KEY` and `DATABASE_URL` are already kept out of git the
same way). Add the new variables to `.env`, and also add them wherever the
deployed app's secrets are configured (the same place `DATABASE_URL` is
currently set for the Neon deployment) — otherwise tracing will work locally
but silently not work on the deployed app.

---

## Step 1 — Add the environment variables

**File:** `.env` (local) and the deployed app's secrets (e.g. Streamlit
Cloud's secrets manager, wherever `DATABASE_URL` currently lives)

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<the key from smith.langchain.com>
LANGCHAIN_PROJECT=interview-intelligence-platform
```

If a `.env.example` file exists in the repo, add these three keys there too
with placeholder values (never a real key) so the setup step is documented for
anyone else who clones the repo.

**Done when:** the three variables exist in both places.

---

## Step 2 — Confirm nothing needs to change in the code

Every LLM call in this project already goes through LangChain
(`ChatGroq` in `models/llm_provider.py`) and every workflow already goes
through LangGraph (`graphs/*.py`). Both libraries read the environment
variables above automatically at call time. **No import, no decorator, no
function call needs to be added anywhere in `rag/`, `agents/`, or `graphs/`.**

Confirm this by checking that `load_dotenv()` (already called in
`models/llm_provider.py` and `database/db.py`) runs before any graph is
invoked — it already does, since it happens at import time.

**Done when:** you've confirmed by reading the code that no source file needs
editing for tracing to work — this step is verification, not implementation.

---

## Step 3 — Verify traces actually appear

Run the app locally (or the deployed version) and do three things:

1. Ask one question in the chat tab.
2. Run one resume check.
3. Complete one theory-round question.

Then open the LangSmith dashboard for the project named in
`LANGCHAIN_PROJECT`. Confirm three separate runs appear, and that clicking
into the chat run shows the retrieve → grade → generate node sequence with
the actual retrieved chunks and the actual prompt sent to Groq.

**Part A is complete when all three runs are visible in the dashboard with
their full node-by-node breakdown.**

---

# PART B — Reasoning panel in the chat UI

## B.1 What this is and why it's cheap

Every fact needed for this already exists in the graph's state by the time
`rag_graph.invoke()` returns — `documents`, `relevant_documents`, `sources`,
and (once Part B of `docs/M8_login_and_agentic_rag.md` is built)
`retry_count` and `sub_questions`. This step does not add any new
computation to the graph. It only takes numbers and lists that are already
being thrown away after the terminal `print()` and displays them to the user
instead.

**Merge this into the existing sources expander from M1 — do not add a
second expander.** `ui/chat.py` already renders a "Sources" expander after
each answer (built in M1). Adding a separate "reasoning" expander next to it
would clutter the UI with two collapsed boxes doing overlapping jobs. Extend
the one that already exists.

## B.2 One gotcha: this must not crash if agentic RAG isn't built yet

If Part B of `docs/M8_login_and_agentic_rag.md` hasn't been implemented,
`result` won't contain `retry_count` or `sub_questions` at all. **Read every
new field with `.get()` and a default, never with `result["field"]`:**

```python
retry_count = result.get("retry_count", 0)
sub_questions = result.get("sub_questions", [])
```

This way the panel just quietly shows less information (no retry line, no
sub-question breakdown) instead of throwing a `KeyError` — regardless of
which order these two bricks get built in.

---

## Step 1 — Extend the existing sources expander

**File:** `ui/chat.py`

Find the existing sources-rendering block from M1. Before the list of
sources, add the reasoning summary:

```python
retrieved_count = len(result.get("documents", []))
kept_count = len(result.get("relevant_documents", []))
retry_count = result.get("retry_count", 0)
sub_questions = result.get("sub_questions", [])

with st.expander(f"Sources ({len(sources)})", expanded=False):
    if len(sub_questions) > 1:
        st.caption("This question was broken into parts:")
        for sub_q in sub_questions:
            st.caption(f"- {sub_q}")

    st.caption(f"Retrieved {retrieved_count} chunks, kept {kept_count} after relevance check.")

    if retry_count > 0:
        st.caption(f"Search was retried {retry_count} time(s) to find better matches.")

    for source in sources:
        st.write(f"{source['file_name']} · page {source['page']} · {source['doc_type']}")
```

Keep the existing per-source rendering exactly as M1 built it — only the
summary lines above are new.

**Done when:** asking a normal question shows the expander with retrieval
counts and sources, and no error occurs even if `retry_count` /
`sub_questions` are missing from the result.

---

## Step 2 — Persist the new fields in chat history

**File:** `ui/chat.py`

The existing pattern (from M1) already stores `sources` alongside each
assistant message in `st.session_state.messages[session_id]` so the expander
survives a rerun. Extend the same stored dict with the new fields:

```python
{
    "role": "assistant",
    "content": answer,
    "sources": sources,
    "retrieved_count": retrieved_count,
    "kept_count": kept_count,
    "retry_count": retry_count,
    "sub_questions": sub_questions,
}
```

When replaying history, read every one of these with `.get(key, default)` —
older messages saved before this brief was implemented won't have these
keys.

**Done when:** switching tabs or triggering a rerun still shows the full
reasoning panel for previously-asked questions, not just the newest one.

---

## Manual verification for Part B

This is UI behavior — verify it by hand in the browser rather than a script:

1. Ask a simple, single-topic question. Expander shows retrieved/kept counts
   and sources; no "broken into parts" line; no "retried" line.
2. Ask the project's six-requirement Data Analyst question (see the earlier
   test question built for M9). Expander shows the "broken into parts" list
   with more than one sub-question.
3. If Part B of `docs/M8_login_and_agentic_rag.md` is not yet built, confirm
   step 1 above still works with no error — this proves the `.get()` defaults
   are doing their job (gotcha B.2).

**Part B is complete when the expander shows correct reasoning info for both
a simple question and a decomposed one, and never crashes regardless of
whether the agentic RAG upgrade has landed yet.**
