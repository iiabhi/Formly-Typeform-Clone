# CLAUDE.md — Project context (read this every session)

## What we're building
A functional clone of Typeform: a form **builder**, form **management** (CRUD + publish),
a public **one-question-at-a-time respondent flow**, and a **results** view.
Full spec, schema, API and the session-by-session plan live in `PLAN.md`.
**We build ONE session (feature) at a time. Only work on the session I name.**

Working product name: **Formly** (do NOT use Typeform's name, logo or assets anywhere in the UI.
We replicate layout, interaction and feel — not branding).

The original assignment is at `docs/ASSIGNMENT.pdf`. `PLAN.md §0` maps every assignment line to a session.
If the plan and the assignment ever disagree, **the assignment wins** — tell me about the conflict.

## Assignment constraints (non-negotiable)
- **Mandated stack:** Frontend **Next.js + TypeScript**. Backend **Python + FastAPI** (assignment allows
  FastAPI or Django; we chose FastAPI). Database **SQLite** with **our own schema design**.
  Do not introduce any other backend language, database, BaaS (Firebase/Supabase) or form library that
  does the core work for us.
- **Original work.** Write all code from scratch for this repo. Never copy or adapt code from existing
  Typeform-clone repositories or templates — plagiarism means disqualification. Using normal libraries is fine.
- **I must understand every line.** Prefer clear, conventional code over clever code. Explain non-obvious parts.
- **UI/UX must look and feel like Typeform** (it is an evaluation criterion of its own) — see Design rules.
- **Respondent flow is public:** `/to/[slug]` works for anyone with the link, no login, on any device.
- **Everything persists** in SQLite: form definitions, questions, settings, responses.
- **Repo** must contain top-level `frontend/` and `backend/` and a `README.md` (setup, tech stack,
  architecture overview, database schema, API overview, assumptions).
- **Seed data** must make the app usable immediately: ≥2 published forms with mixed question types and existing responses.

## Stack
- `frontend/` — Next.js 14+ (App Router), TypeScript (strict), Tailwind CSS,
  Framer Motion (transitions), @dnd-kit (drag-and-drop), TanStack Query (server state),
  Zustand (builder local state), Sonner (toasts), lucide-react (icons)
- `backend/` — Python 3.11+, FastAPI, SQLAlchemy 2.0 (typed `Mapped[]` models), Pydantic v2, SQLite, pytest
- No auth. A single default creator (user id 1) is assumed for all creator routes (allowed by the assignment).
  Public form-fill routes need no auth at all.

## Repo layout
```
frontend/
  src/app/                 # routes (see PLAN.md §5)
  src/components/ui/       # generic primitives (Button, Modal, Toggle, Dropdown, Menu...)
  src/components/questions/# SHARED question renderers (used by builder preview AND respondent flow)
  src/components/builder/  # builder-only components
  src/components/respondent/
  src/components/results/
  src/lib/api/             # typed API client, one file per resource
  src/lib/validation.ts    # client-side answer validation (mirrors backend rules)
  src/types/               # shared TS types matching backend schemas
backend/
  app/main.py
  app/core/config.py, app/db.py
  app/models/              # SQLAlchemy models
  app/schemas/             # Pydantic request/response models
  app/routers/             # thin HTTP layer only
  app/services/            # business logic (validation, duplication, stats, csv)
  app/seed.py
  tests/
```

## Rules
1. **Routers are thin.** Logic goes in `services/`. Routers validate input, call a service, return a schema.
2. **One source of truth for question types.** The type list + per-type `properties` shape is defined once
   in backend (`app/models/enums.py` + `schemas/question.py`) and mirrored once in `frontend/src/types/question.ts`.
3. **Question renderers are shared.** The builder's live preview and the public form use the same
   components from `components/questions/`. Never duplicate rendering logic.
4. **Server validation is authoritative.** Client validation exists for UX only.
5. Keep components small (< ~200 lines). Extract hooks (`useXxx`) for logic.
6. No `any` in TypeScript. No unused code. No commented-out code.
7. After finishing a session: run backend tests (`pytest`), run `npm run lint && npm run build` in frontend,
   update the **Progress** checklist at the bottom of `PLAN.md`, and suggest a commit message.
8. When done, give me a short explanation of what you built and why (I must be able to explain every line in an interview).
9. If something in the plan seems wrong, tell me before changing it — don't silently deviate.
10. Before ending a session, re-check that session's rows in `PLAN.md §0` (requirements traceability) and
    confirm each one is actually working, not just coded.

## Evaluation criteria we are optimising for
Functionality (builder + respondent flow above all) · UI/UX similarity to Typeform · Database design ·
Backend/API design · Code quality · Code modularity (separation of concerns, reusable components) ·
Code understanding (I explain it in an interview).

## Commands
- Backend: `cd backend && uvicorn app.main:app --reload --port 8000` · tests: `pytest -q` · seed: `python -m app.seed`
- Frontend: `cd frontend && npm run dev` (port 3000) · `npm run lint` · `npm run build`
- Env: frontend uses `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) and `NEXT_PUBLIC_APP_URL`
  (default `http://localhost:3000`, used to build shareable links `${APP_URL}/to/${slug}`);
  backend uses `DATABASE_URL` (default `sqlite:///./formly.db`), `CORS_ORIGINS` and `UPLOAD_DIR` (bonus file upload).

## Design rules (Typeform look & feel)
- Match the reference screenshots in `/docs/screenshots/` when present. When in doubt, look at them, don't guess.
- Respondent default theme: white background, near-black question text, a single **accent color**
  (default deep blue, ~`#0445AF`) for answers, buttons, numbers, progress bar and selected states.
- Lots of whitespace, large type, one focal element per screen. Builder UI is neutral grey/black/white.
- Every async action gets feedback: loading state + success/error toast.
