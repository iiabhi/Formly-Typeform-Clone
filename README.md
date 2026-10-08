# Formly

A Typeform-style form builder: create forms, share a public one-question-at-a-time link, and review responses.

**Stack:** Next.js + TypeScript (frontend) · FastAPI (Python) backend · SQLite.

> Full README (setup, architecture, schema, API overview, assumptions) is written in Session 12.

## Quick start

```bash
# backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend && npm install && cp .env.example .env.local && npm run dev
```
