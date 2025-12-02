# RAG Agent Platform - Claude Instructions

## Project Overview
This is a RAG (Retrieval-Augmented Generation) Agent Platform built with:
- **Frontend**: SvelteKit + Tailwind CSS + Inlang (i18n)
- **Backend**: FastAPI (Python)
- **LLM Proxy**: LiteLLM
- **Database**: PostgreSQL
- **Vector Store**: ChromaDB

## Directory Structure
- `/frontend` - SvelteKit frontend application
- `/backend` - FastAPI backend (not started)
- `/litellm-container` - LiteLLM Docker setup
- `/.docs` - Project documentation

## Task Tracking Rules

### IMPORTANT: Update Todo List After Completing Tasks
When you complete any task that corresponds to an item in `.docs/04-todos.md`:
1. **Immediately update the todo list** by changing `[ ]` to `[x]`
2. Update the progress overview table if a component status changes
3. Update the "Current Focus" section if needed

### Example
Before:
```
- [ ] Setup PostgreSQL in docker-compose
```

After completing:
```
- [x] Setup PostgreSQL in docker-compose
```

## Development Guidelines
- Always write code and comments in English
- Follow existing code style and patterns
- Test changes before marking tasks complete
