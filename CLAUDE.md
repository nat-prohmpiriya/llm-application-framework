# RAG Agent Platform - Claude Code Instructions

## Quick Reference

Load context as needed to reduce tokens:

| Context Needed | File to Read |
|----------------|--------------|
| **Frontend (Svelte 5)** | `.claude/frontend.md` |
| **Backend (FastAPI)** | `.claude/backend.md` |
| **API Routes** | `.claude/api-routes.md` |
| **Services Layer** | `.claude/services.md` |
| **Testing** | `.claude/testing.md` |
| **Full Spec** | `.docs/02-spec.md` |
| **Todo List** | `.docs/04-todos.md` |

## Project Overview

**RAG Agent Platform** - Full-stack AI document retrieval & chat system.

| Layer | Technology |
|-------|------------|
| Frontend | SvelteKit 2.x + Svelte 5 (Runes) + Tailwind v4 + shadcn-svelte |
| Backend | FastAPI + Python 3.12+ + SQLAlchemy async + PostgreSQL |
| LLM | LiteLLM Proxy (OpenAI, Gemini, Groq) |
| Vector | ChromaDB |
| Auth | JWT + Refresh Token |
| Tracing | OpenTelemetry + Jaeger |

## Directory Structure

```
/
├── frontend/          # SvelteKit app
├── backend/           # FastAPI app
├── infra/             # Docker configs
├── .docs/             # Specifications
└── .claude/           # Detailed instructions (load as needed)
```

## Critical Rules

### Svelte 5 (MUST USE)
```svelte
<!-- ✅ Correct -->
let count = $state(0);
let doubled = $derived(count * 2);
let { name } = $props();
{@render children()}

<!-- ❌ Wrong (Svelte 4) -->
let count = 0;
$: doubled = count * 2;
export let name;
<slot />
```

### Python Type Hints (MUST USE)
```python
# ✅ Correct
async def get_user(user_id: int) -> User | None:
    ...

# ❌ Wrong
async def get_user(user_id):
    ...
```

### API Response (MUST WRAP)
```python
return BaseResponse(trace_id=ctx.trace_id, data=UserResponse.model_validate(user))
```

## Commands

```bash
# Backend
cd backend && uv run uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Docker
docker-compose up -d
```

## Task Tracking

When completing tasks, update `.docs/04-todos.md`:
- Change `[ ]` to `[x]` for completed items
