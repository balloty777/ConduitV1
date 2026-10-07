# Conduit

**An AI agent orchestration platform for automating operational workflows across teams — with a human always in the loop.**

🔗 **Live demo:** [conduitv1.onrender.com](https://conduitv1.onrender.com)

---

## What Conduit is

Conduit is a multi-agent automation platform built around a single orchestration core. A **Supervisor graph** receives a plain-language request, classifies it, hands it to the right department agent, and — before anything real happens — pauses and waits for a human to approve or reject it.

Right now Conduit handles three departments end-to-end:

| Department | What the agent does | Example request |
|---|---|---|
| 🎯 **Marketing** | Drafts social content, routes it for review, schedules it once approved | *"Write a LinkedIn post announcing our new pricing tier"* |
| 📈 **Sales** | Creates leads and drafts follow-up messages | *"Follow up with the lead from yesterday's demo call"* |
| 🛠 **Tech** | Logs tickets and proposes fixes — approving a ticket automatically triggers a proposed fix, which needs its own approval | *"Log a bug: users can't reset their password"* |

The aim isn't to remove people from the loop — it's the opposite. Every consequential action (publishing, scheduling, closing a ticket) stops for human sign-off before it happens. The interesting engineering problem Conduit solves is: **how do you pause a running multi-agent workflow for an indefinite amount of time, let a human act on it whenever they get to it, and resume exactly where it left off** — without losing state, without re-running work that's already done, and with a full audit trail of what happened.

---

## Why I built it

I wanted a project that went past "call an LLM and print the result" and into the part that actually matters in production: durable state, human oversight, observability, and a system that fails safely instead of silently. Conduit is my answer to that — a from-scratch build covering the full stack from the database up to a live dashboard.

---

## Architecture

```
Request
  │
  ▼
┌─────────┐     ┌──────────┐     ┌─────────────────┐     ┌───────────────┐
│  entry  │ ──▶ │  router  │ ──▶ │ department agent │ ──▶ │ approval_wait │
└─────────┘     └──────────┘     └─────────────────┘     └───────┬───────┘
                      │                                          │
                 (Jev classifies                        ┌────────┴────────┐
                  the request)                           ▼                 ▼
                                                      approved          rejected
                                                          │                 │
                                                   schedule / done    back to agent
                                                   (or chains into    with feedback,
                                                    a follow-up        drafts again
                                                    approval, e.g.
                                                    ticket → fix)
```

Every node writes its own step to a durable execution log, so a full run — including every rejected draft and every regeneration — can be reconstructed after the fact.

### The core engineering problem: pausing mid-workflow

This is the part of the project I'm most proud of. When an agent finishes a draft, the graph doesn't just return a response — it **suspends itself**, using LangGraph's `interrupt()` mechanism backed by a **Postgres-backed checkpointer**. The workflow's entire state is persisted to the database. A human can approve or reject it five seconds later, or five days later, and the graph resumes from exactly that point — same execution, same history, no re-running of work already done.

Rejecting isn't a dead end, either: the rejection reason flows back into the agent's next attempt, so the LLM revises its draft with actual feedback instead of starting blind.

### Why approvals are a separate, generic concept

Rather than bolting "needs approval" onto each department's data model, Conduit has one shared `ApprovalRequest` entity that just references *what* is pending (`subject_type` + `subject_id`) and *which run it belongs to*. One approval surface, one audit trail, reused identically by Marketing, Sales, and Tech — and ready for any future department without touching the approval logic at all.

---

## Tech stack

| Layer | Tools |
|---|---|
| **Orchestration** | [LangGraph](https://www.langchain.com/langgraph) — the Supervisor graph, state management, and `interrupt()`/`Command(resume=...)` for the human-in-the-loop pause/resume cycle |
| **Agent framework** | [LangChain](https://www.langchain.com) for structured LLM output and tool binding |
| **Routing model** | [**Jev**](https://openrouter.ai) (TypeSafe, via OpenRouter) — a decision model purpose-built for typed classification, used by the router to pick which department handles a request with a confidence score, rather than spending a general-purpose chat model on what's really a classification task |
| **Drafting model** | OpenAI **GPT-5.4** — generates the actual content/replies/fixes departments produce |
| **Agent ↔ tool boundary** | [MCP](https://modelcontextprotocol.io) (Model Context Protocol) via FastMCP — each department exposes a small, deliberately narrow set of agent-facing tools (create/read only; nothing destructive is ever agent-reachable) |
| **API** | FastAPI |
| **Persistence** | PostgreSQL, SQLAlchemy, Alembic migrations |
| **Checkpointing** | `langgraph-checkpoint-postgres` — durable graph state, enabling true pause/resume |
| **Frontend** | Vanilla JS/HTML/CSS dashboard — zero build step, so it's as easy to run as opening a file |
| **Deployment** | Render |

---

## Design principles

- **MCP is agent-facing, HTTP is human-facing.** Agents can create and read. Humans update, delete, schedule, approve, and reject. The agent is never one tool call away from an irreversible action.
- **Approval is an event, not a status.** Content doesn't carry a "pending approval" state of its own — the `ApprovalRequest` table is the single source of truth for what's awaiting a decision, keeping each department's own data model simple.
- **One execution, many attempts.** A rejection doesn't start a new workflow — it resumes the same one, so the full history of a request (every draft, every piece of feedback) lives under a single, traceable execution ID.
- **Services own transactions, repositories don't.** A strict, consistent boundary: repositories `flush()`, services `commit()`/`rollback()`. It sounds pedantic until you need to roll back a multi-step action atomically — then it's the only thing that saves you.

---

## Testing

Conduit has a real `pytest` suite, not just manual scripts — including full end-to-end integration tests that run the actual graph through a complete **draft → reject → regenerate → approve** cycle against a real database, for all three departments. One test specifically covers the tech ticket → auto-generated fix → approval chain.

---

## Getting started

```bash
git clone <https://github.com/balloty777/ConduitV1>
cd conduit

# install dependencies
pip install -e .

# configure environment
cp .env.example .env
# fill in: database_url, openai_api_key, openrouter_api_key, openai_model, jev_model, jev_base_url

# run migrations
alembic upgrade head

# start the API
uvicorn main:app --reload
```

Then open `frontend/index.html` (or serve it statically) pointed at your running API.

To kick off a workflow:

```bash
curl -X POST http://localhost:8000/executions \
  -H "Content-Type: application/json" \
  -d '{"request": "Draft a LinkedIn post announcing our new pricing tier"}'
```

Watch it show up under `/approvals`, then approve or reject it from the dashboard.

---

## 🚧 Work in progress: v2

Conduit v1 proves the orchestration core end-to-end. Actively being worked on next:

- **RAG** — per-department retrieval so agents draft with real context (past tickets, CRM history, brand guidelines) instead of a bare prompt
- **Guardrails** — automated output validation (tone, PII, factual grounding) before a draft ever reaches a human
- **Observability** — LangSmith tracing layered on top of the existing execution/approval audit trail
- **Hardening** — rate limits, per-run cost caps, and a kill switch
- **Auth** — replacing the current operator-ID pattern with real authenticated sessions

---

