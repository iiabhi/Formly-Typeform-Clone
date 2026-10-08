# PLAN.md — Formly (Typeform clone) build plan

> How to use this file: start each Claude Code session with
> **"Read CLAUDE.md and PLAN.md. We are doing Session N only."** then paste that session's prompt.
> Use plan mode first (Shift+Tab) on big sessions (5, 6, 7, 8), review the plan, then let it build.
> Commit at the end of every session. Start a fresh session for the next one.

---

## 0. Requirements traceability (every line of the assignment → where it's built)

Tick the ✔ column only after verifying in the running app.

**Technical stack**
| Assignment requirement | Where | ✔ |
|---|---|---|
| Frontend: Next.js (TypeScript) | S0 | |
| Backend: Python with FastAPI | S0, S2, S3 | |
| Database: SQLite, own schema design | S1 (§2) | ✔ |
| Respondent flow is real & shareable, no auth to fill | S3 public API, S6 `/to/[slug]`, S12 deployed | |

**1. Form Builder**
| Requirement | Where | ✔ |
|---|---|---|
| Create form with title + ordered list of questions | S2, S4, S5 | |
| Add questions | S2, S5 | |
| Edit questions (inline) | S2, S5, S8 | |
| Reorder questions (drag-and-drop) | S2 order endpoint, S8 | |
| Delete questions | S2, S5 | |
| Types: short text, long text, multiple choice, dropdown, email, number, yes/no, rating | S1 enums, S5 editor, S6 renderers | |
| Per-question: required toggle | S5 | |
| Per-question: description / help text | S5 | |
| Live preview of the form | S8 canvas + full preview modal | |

**2. Form Management (CRUD)**
| Requirement | Where | ✔ |
|---|---|---|
| List creator's forms with status (draft/published) + response count | S2, S4 | |
| Create form | S2, S4 | |
| Rename form | S2, S4 (dashboard + builder breadcrumb) | |
| Duplicate form | S2, S4 | |
| Delete form | S2, S4 | |
| Publish / unpublish | S2, S8 | |
| Generates a shareable public link | S2 slug, S8 share modal + `/share` page | |
| All form definitions persist | S1, S2 | S1 ✔ |

**3. Respondent Flow**
| Requirement | Where | ✔ |
|---|---|---|
| One question at a time, full-screen | S6 | |
| Smooth transitions between questions | S7 | |
| Keyboard navigation (Enter / arrows to advance) | S7 | |
| Progress indicator | S7 | |
| Client validation (required, email, number, …) | S6 `lib/validation.ts` | |
| Server validation (same rules) | S3 `answer_validation.py` | |
| Submit stores the response | S3, S6 | |
| Thank-you screen | S6, S10 | |
| No login required | S3, S6 | |

**4. Results / Responses**
| Requirement | Where | ✔ |
|---|---|---|
| Per-form responses view (table/list) | S3, S9 | |
| View an individual response in full | S3, S9 drawer | |
| Basic summary stats per question (counts for choice questions etc.) | S3 stats_service, S9 | |
| All responses persist | S1, S3 | S1 ✔ |

**5. Typeform Experience**
| Requirement | Where | ✔ |
|---|---|---|
| Conversational one-at-a-time fill UI with transitions | S6, S7 | |
| Clean builder layout with live preview | S5, S8 | |
| Forms, modals, inline editing | S4, S5, S8 | |
| Notifications / toasts | S0 Toaster, every session | |
| Settings placeholders: theme | S10 (implemented, exceeds placeholder) | |
| Settings placeholders: thank-you screen | S5, S10 | |
| Feels like Typeform, not a generic multi-field form | S7, S10 polish vs screenshots | |

**Mocked / placeholder sections ("Coming soon")**
| Requirement | Where | ✔ |
|---|---|---|
| Advanced logic jumps / branching | S5 settings "Logic" → Coming soon (basic branching = bonus C) | |
| Integrations / webhooks | S4 `/connect` page + workspace sidebar | |
| Team collaboration & sharing | S4 workspace sidebar "Team" + S10 | |
| Payment question type | S10 add-question modal "Soon" badge | |
| File-upload question type | S10 "Soon" badge (or real, bonus D) | |
| Simplified auth: default logged-in creator | S0/S2 `get_current_user` → user 1, avatar in sidebar | |

**Bonus (optional)**
| Requirement | Where | ✔ |
|---|---|---|
| Logic jumps / conditional branching | S11-C | |
| Custom themes (colors, fonts, background) | S10 | |
| Export responses as CSV | S3 endpoint, S9 button | |
| Partial-response tracking / completion rate | S11-A | |
| File-upload question type | S11-D | |
| Dark mode | S11-B | |

**Important notes & deliverables**
| Requirement | Where | ✔ |
|---|---|---|
| UI totally resembles Typeform (studied before starting) | screenshots in `docs/screenshots/` before S4; S7, S10 | |
| Seed: a couple of published forms, mixed types, existing responses | S1 | ✔ |
| Own database schema (evaluated) | S1, design decisions in README | S1 ✔ (README in S12) |
| README: setup, tech stack, architecture overview, DB schema, API overview, assumptions | S12 | |
| Original work, no copied repos | CLAUDE.md rule, all sessions | |
| Public GitHub repo containing `frontend/` and `backend/` | S0 layout, S12 | |
| Hosted, working demo link | S12 | |
| Submit GitHub link + deployed link | §9 submission checklist | |

---

## 1. Scope recap

| Area | Must have |
|---|---|
| Builder | title, ordered questions, add / edit / reorder (DnD) / delete, 8 types, required toggle, description, live preview |
| Management | list forms w/ status + response count, create / rename / duplicate / delete, publish / unpublish, share link |
| Respondent | one question per screen, animated transitions, Enter / arrows, progress bar, client + server validation, thank-you screen, no login |
| Results | responses table, single response view, per-question summary stats |
| Feel | toasts, modals, inline editing, settings placeholders (theme, thank-you screen), "Coming soon" for logic/integrations/team/payment/file upload |
| Bonus (if time) | CSV export, completion rate (partial responses), custom themes, dark mode, basic branching, file-upload question |

Question types: `short_text`, `long_text`, `multiple_choice`, `dropdown`, `email`, `number`, `yes_no`, `rating`.

---

## 2. Database schema (SQLite via SQLAlchemy)

```
users
  id              INTEGER PK
  name            TEXT NOT NULL
  email           TEXT NOT NULL UNIQUE
  created_at      DATETIME NOT NULL

forms
  id              TEXT PK            -- uuid4
  owner_id        INTEGER NOT NULL FK -> users.id ON DELETE CASCADE
  title           TEXT NOT NULL DEFAULT 'My new form'
  slug            TEXT NOT NULL UNIQUE  -- short random id, used in public URL /to/{slug}
  status          TEXT NOT NULL CHECK (status IN ('draft','published')) DEFAULT 'draft'
  theme           JSON NOT NULL      -- {accent, background, question_color, font}
  thank_you_title TEXT NOT NULL DEFAULT 'Thanks for completing this form'
  thank_you_description TEXT NULL
  published_at    DATETIME NULL
  created_at      DATETIME NOT NULL
  updated_at      DATETIME NOT NULL
  INDEX (owner_id, updated_at)

questions
  id              TEXT PK            -- uuid4
  form_id         TEXT NOT NULL FK -> forms.id ON DELETE CASCADE
  type            TEXT NOT NULL CHECK (type IN (...8 types...))
  title           TEXT NOT NULL DEFAULT ''
  description     TEXT NULL
  required        BOOLEAN NOT NULL DEFAULT 0
  position        INTEGER NOT NULL   -- 0-based order within form
  properties      JSON NOT NULL DEFAULT '{}'   -- type-specific, see below
  created_at, updated_at
  INDEX (form_id, position)

question_options                     -- only for multiple_choice & dropdown
  id              TEXT PK
  question_id     TEXT NOT NULL FK -> questions.id ON DELETE CASCADE
  label           TEXT NOT NULL
  position        INTEGER NOT NULL
  INDEX (question_id, position)

responses
  id              TEXT PK
  form_id         TEXT NOT NULL FK -> forms.id ON DELETE CASCADE
  status          TEXT NOT NULL CHECK (status IN ('in_progress','completed')) DEFAULT 'completed'
  started_at      DATETIME NOT NULL
  submitted_at    DATETIME NULL
  user_agent      TEXT NULL
  INDEX (form_id, submitted_at)

answers
  id              TEXT PK
  response_id     TEXT NOT NULL FK -> responses.id ON DELETE CASCADE
  question_id     TEXT NOT NULL FK -> questions.id ON DELETE CASCADE
  text_value      TEXT NULL          -- short_text, long_text, email
  number_value    REAL NULL          -- number, rating
  boolean_value   BOOLEAN NULL       -- yes_no
  UNIQUE (response_id, question_id)

answer_choices                       -- selected options for multiple_choice / dropdown
  answer_id       TEXT NOT NULL FK -> answers.id ON DELETE CASCADE
  option_id       TEXT NOT NULL FK -> question_options.id ON DELETE CASCADE
  PRIMARY KEY (answer_id, option_id)
```

**`questions.properties` per type**
| type | properties |
|---|---|
| short_text / long_text | `{ placeholder?: str, max_length?: int }` |
| email | `{ placeholder?: str }` |
| number | `{ min?: number, max?: number }` |
| multiple_choice | `{ allow_multiple: bool, randomize: bool }` |
| dropdown | `{ randomize: bool }` |
| yes_no | `{}` |
| rating | `{ steps: 3..10 (default 5), shape: 'star' }` |

**Design decisions (put these in the README, be ready to explain):**
- Typed answer columns (`text_value`, `number_value`, `boolean_value`) + `answer_choices` join table instead of one JSON blob → summary stats are plain SQL `GROUP BY`/`COUNT`/`AVG`, and choice answers keep referential integrity.
- Options are a table (not JSON) because answers reference them by FK.
- `properties` is JSON because it's type-specific config that is never queried across forms.
- `position` integer + a single "reorder" endpoint that rewrites positions in one transaction.
- `UNIQUE(response_id, question_id)` makes upserting partial answers safe (bonus feature).
- Deleting a question cascades its answers; the builder warns if the form already has responses.
- UUID ids for forms/questions/responses so public URLs and ids are not guessable; `slug` is a separate short id for nice share links.
- Enable SQLite FK enforcement: `PRAGMA foreign_keys=ON` on every connection.

---

## 3. Validation rules (same rules client & server)

| type | rule | error message |
|---|---|---|
| any required | non-empty | "Please fill this in" |
| multiple_choice/dropdown required | ≥1 option | "Oops! Please make a selection" |
| email | basic RFC-ish regex | "Hmm... that email doesn't look quite right" |
| number | numeric, within min/max | "Please enter a number" / "Must be between X and Y" |
| rating | integer 1..steps | — |
| choice | option ids must belong to that question; single unless allow_multiple | 422 |
| short_text | ≤ max_length (default 255) | — |
| long_text | ≤ max_length (default 5000) | — |

Server returns `422` with `{ "detail": [{ "question_id": "...", "message": "..." }] }`.

---

## 4. API (FastAPI, prefix `/api`)

**Creator — forms**
| Method | Path | Notes |
|---|---|---|
| GET | `/forms` | list: id, title, status, response_count, updated_at. `?q=` search, `?sort=` |
| POST | `/forms` | create (optional `title`) → full form |
| GET | `/forms/{id}` | full form incl. ordered questions + options |
| PATCH | `/forms/{id}` | title, theme, thank_you_* |
| DELETE | `/forms/{id}` | 204 |
| POST | `/forms/{id}/duplicate` | deep copy (questions + options, not responses), title "X (copy)", status draft |
| POST | `/forms/{id}/publish` | 400 if form has 0 questions or any question has empty title |
| POST | `/forms/{id}/unpublish` | |

**Creator — questions**
| Method | Path | Notes |
|---|---|---|
| POST | `/forms/{id}/questions` | `{type, position?}` → created with sensible defaults (e.g. 2 options for choice) |
| PATCH | `/questions/{qid}` | title, description, required, type, properties, `options: [{id?, label}]` (full replace, keeps ids that are sent) |
| DELETE | `/questions/{qid}` | re-compacts positions |
| POST | `/questions/{qid}/duplicate` | inserted right after |
| PUT | `/forms/{id}/questions/order` | `{question_ids: [...]}` must be exact set of form's questions |

**Public (no auth)**
| Method | Path | Notes |
|---|---|---|
| GET | `/public/forms/{slug}` | 404 unless published. Returns only what a respondent needs |
| POST | `/public/forms/{slug}/responses` | `{answers: [{question_id, value}]}` → validates all, stores, 201 |

**Results**
| Method | Path | Notes |
|---|---|---|
| GET | `/forms/{id}/responses` | paginated `?page=&page_size=`, newest first, answers flattened for table |
| GET | `/forms/{id}/responses/{rid}` | full single response |
| DELETE | `/forms/{id}/responses/{rid}` | |
| GET | `/forms/{id}/summary` | per question: answered count; choice → counts + %; yes_no → yes/no counts; rating/number → avg, min, max, distribution; text → latest 5 answers |
| GET | `/forms/{id}/responses.csv` | bonus |

---

## 5. Frontend routes

| Route | Screen |
|---|---|
| `/` | redirect → `/workspace` |
| `/workspace` | forms dashboard |
| `/forms/[id]/create` | builder (top tabs: Create · Connect · Share · Results) |
| `/forms/[id]/connect` | "Coming soon" (integrations/webhooks) |
| `/forms/[id]/share` | share link, copy button, publish state |
| `/forms/[id]/results` | sub-tabs: Summary · Responses |
| `/to/[slug]` | public respondent flow (no app chrome) |

---

## 6. Typeform UX reference (what "feels like Typeform" means)

Collect 10–15 screenshots of real Typeform into `docs/screenshots/` before Session 4 (workspace, builder, add-question modal, a live form's text / choice / rating / yes-no screens, error state, thank-you screen, results summary & responses table). Claude Code can read images — reference them in prompts.

**Respondent flow**
- Full viewport, content vertically centred, max-width ~720px, left-aligned.
- Question header: small accent-colored number + arrow (`1 →`), then question title (~24px, regular weight), required `*`, description below in lighter/smaller text.
- Text inputs: no box, just a large text line with a bottom border in accent color; placeholder "Type your answer here...".
- Below input: accent button **OK ✓** plus hint "press **Enter ↵**". Long text: "**Shift ⇧ + Enter ↵** to make a line break".
- Choices: stacked boxes with a lettered key badge (A, B, C...) — pressing the letter selects. Selected = tinted fill + check. Single-select auto-advances after a short delay (~400ms) with a blink on the chosen item. Multi-select shows "Choose as many as you like".
- Yes/No: two boxes, keys Y / N. Rating: row of stars (or numbered boxes), keys 1–9.
- Dropdown: text input with filterable option list below.
- Error: small badge below the input with a warning icon and the message; red-ish tint.
- Transitions: current question slides/fades **up** and the next slides in from below; reverse on going back (~300–400ms ease).
- Chrome: thin progress bar at top; bottom-right a pair of up/down chevron buttons; "x of y answered" style progress.
- Keyboard: Enter = OK/next, ↑/↓ = prev/next, letters/digits select options, Tab works.
- Thank-you screen: centred title + description, same theme.

**Builder**
- Top bar: breadcrumb (Workspace › Form title, title editable inline), centre tabs Create / Connect / Share / Results, right: Preview (eye) + **Publish** button.
- Left sidebar (~260px): "Content" list of questions, each row = colored type icon with number + truncated title; drag handle; active row highlighted; "+" button to add; endings section showing thank-you screen.
- Centre: canvas rendering the selected question exactly as the respondent sees it (this IS the live preview), with title/description editable inline on the canvas, options editable inline.
- Right panel (~300px): "Question" settings — type switcher dropdown, Required toggle, type-specific settings (allow multiple, randomize, min/max, rating steps), "Logic" → Coming soon.
- Add question: modal with categorised type list (each type with colored icon).
- Autosave with subtle "Saving… / Saved" indicator. Toasts on publish, delete, duplicate, errors.

**Workspace**
- Left sidebar: default creator's avatar + name (simplified auth), "My workspace" + placeholder items
  (Team & sharing, Integrations → Coming soon).
- Main: header with "+ Create form" button, search, sort; forms as list/grid with title, status pill (Draft/Published), responses count, last updated, `⋯` menu (Rename, Duplicate, Copy link, Delete). Confirm modal on delete. Empty state.

---

## 7. Sessions

Each session = one Claude Code session. Prompt blocks are ready to paste after the opening line.

---

### Session 0 — Scaffolding (≈30 min)
```
Set up the monorepo exactly as described in CLAUDE.md "Repo layout".
Backend: FastAPI app with /api/health, config via pydantic-settings (DATABASE_URL, CORS_ORIGINS),
SQLAlchemy engine/session in app/db.py with PRAGMA foreign_keys=ON, pytest configured with an
in-memory/temporary SQLite fixture, requirements.txt, ruff config.
Frontend: Next.js App Router + TypeScript strict + Tailwind + ESLint, install framer-motion,
@dnd-kit/core, @dnd-kit/sortable, @tanstack/react-query, zustand, sonner, lucide-react.
Add a QueryClient provider and Toaster in the root layout, a typed fetch wrapper in src/lib/api/client.ts
reading NEXT_PUBLIC_API_URL (and NEXT_PUBLIC_APP_URL in src/lib/config.ts for share links),
and a home page that calls /api/health and shows the result.
Add .gitignore files (ignore *.db, .env, node_modules, .next, __pycache__, uploads/), .env.example files
for both apps, a docs/ folder with docs/screenshots/.gitkeep, and a root README stub.
Initialise git with a first commit. Do NOT build any features yet.
```
Before starting: copy the assignment PDF into `docs/ASSIGNMENT.pdf` (CLAUDE.md points to it).

✅ Done when: both servers run, home page shows "ok", `pytest` passes, `npm run build` passes,
repo has top-level `frontend/` and `backend/`.

---

### Session 1 — Database models + seed (≈1 hr)
```
Implement the database schema from PLAN.md §2 with SQLAlchemy 2.0 typed models in backend/app/models/,
including the enums in app/models/enums.py, all FKs with ON DELETE CASCADE, CHECK constraints,
indexes and the UNIQUE constraints. Create tables on startup (Base.metadata.create_all).
Write app/seed.py (idempotent: wipes and reseeds) that creates:
- default user (id=1, "Alex Creator")
- Form 1 "Customer Feedback Survey" (published) using ALL 8 question types, with ~25 completed responses
  with realistic varied answers spread over the last 30 days
- Form 2 "Event Registration" (published), 6 questions, ~12 responses
- Form 3 "Product Ideas" (draft), 3 questions, 0 responses
Write model tests: cascade deletes work, unique constraints enforced, options ordered by position.
Explain the schema design decisions to me at the end.
```
✅ Done when: `python -m app.seed` works, DB inspectable, tests pass.

---

### Session 2 — Creator API: forms + questions (≈1.5 hr)
```
Implement the "Creator — forms" and "Creator — questions" endpoints from PLAN.md §4.
Structure: Pydantic schemas in app/schemas/ (separate Create/Update/Out models; properties validated
per question type with a discriminated union or a validator), business logic in app/services/form_service.py
and question_service.py, thin routers in app/routers/forms.py and questions.py.
All creator routes use a get_current_user dependency that returns user id 1.
Details: duplicate is a deep copy; reorder runs in one transaction and rejects mismatched id sets;
delete re-compacts positions; changing a question's type resets incompatible properties/options;
publish rejects empty forms or untitled questions with a clear 400 message; slug is a short random
url-safe string generated on create.
Write pytest tests for every endpoint including error cases.
```
✅ Done when: all endpoints work in `/docs`, tests pass.

---

### Session 3 — Public + results API (≈1.5 hr)
```
Implement the "Public" and "Results" endpoints from PLAN.md §4 (including responses.csv).
Put answer validation in app/services/answer_validation.py implementing PLAN.md §3 exactly, returning
all errors at once as 422 { detail: [{question_id, message}] }. Unknown question ids → 422.
The public GET must 404 for drafts and must not leak internal fields (owner, timestamps).
Submission stores response + answers + answer_choices in one transaction.
Summary stats in app/services/stats_service.py using SQL aggregation (GROUP BY / COUNT / AVG), not Python loops over all rows.
CSV: one row per response, one column per question (in position order), choices joined with ", ".
Write tests: valid submit, each validation failure, draft form 404, summary correctness against seed-like data.
```
✅ Done when: can submit via `/docs` and see it in summary; tests pass. **Backend is now complete.**

---

### Session 4 — Frontend foundation + Workspace dashboard (≈1.5 hr)
```
Look at the workspace screenshots in docs/screenshots/.
1. Create src/types/ mirroring the backend schemas, and typed API modules in src/lib/api/ (forms, questions,
   public, results) with TanStack Query hooks in src/lib/queries/.
2. Build UI primitives in src/components/ui/: Button (variants), IconButton, Modal, ConfirmDialog, Toggle,
   Dropdown/Menu, Input, Tabs, StatusPill, Spinner, EmptyState, ComingSoon.
3. Build /workspace per PLAN.md §6 "Workspace": sidebar, header, search, sort, list of forms with status pill,
   response count, updated time, ⋯ menu with Rename (inline), Duplicate, Copy link (published only), Delete
   (confirm modal). "+ Create form" creates and navigates to /forms/[id]/create.
   Optimistic updates where sensible, toast on every action, loading skeletons, empty state.
4. Create the shared form-level layout for /forms/[id]/* with the top bar (breadcrumb with inline-editable
   title, Create/Connect/Share/Results tabs, Publish button). Connect page = ComingSoon.
```
✅ Done when: dashboard fully works against real backend.

---

### Session 5 — Builder: layout, add/edit questions, settings (≈2 hr) — use plan mode
```
Look at the builder screenshots in docs/screenshots/.
Build /forms/[id]/create per PLAN.md §6 "Builder" — EXCEPT drag-and-drop and the polished live preview
(those are Session 7). For now the centre canvas can be a simple editable view.
- Zustand store for builder UI state (selected question id, save status). Server state stays in TanStack Query.
- Left sidebar: question list with colored type icons + numbers, select on click, "+" opens Add Question modal
  (categorised types with icons). Delete and duplicate via row hover menu (warn if form has responses).
  Thank-you screen entry at the bottom (selecting it shows editable thank-you title/description).
- Right settings panel: type switcher, Required toggle, description toggle, and per-type settings
  (allow_multiple, randomize, min/max, rating steps). Logic → ComingSoon.
- Option editor for multiple_choice/dropdown: add, edit inline, delete, Enter adds next option.
- Autosave: debounced (~600ms) PATCH, "Saving…/Saved" indicator in top bar, error toast + retry.
Put a single question-type registry in src/lib/questionTypes.ts (label, icon, color, default properties) and use it everywhere.
```
✅ Done when: can build a full form with all 8 types and everything persists on refresh.

---

### Session 6 — Respondent flow: core (≈2 hr) — use plan mode
```
Look at the respondent screenshots in docs/screenshots/.
1. Build the SHARED question renderers in src/components/questions/ (one component per type + a
   QuestionRenderer switch). Props: question, value, onChange, error, theme, mode ('live' | 'preview').
   They must be pure/controlled so the builder can reuse them later.
2. Build /to/[slug] per PLAN.md §6 "Respondent flow": fetch public form, a useFormRunner hook managing
   current index, answers, errors, direction, submit. Client validation in src/lib/validation.ts
   (mirrors PLAN.md §3). On submit, map server 422 errors back to the question and jump to it.
3. Thank-you screen with the form's thank-you text. Friendly 404 / "this form is closed" screen for
   unpublished forms. Apply form.theme via CSS variables.
Keyboard and animations can be basic in this session; Session 7 polishes them.
```
✅ Done when: can fill & submit each seeded form end to end; invalid input is blocked on both sides.

---

### Session 7 — Respondent flow: the Typeform feel (≈1.5 hr)
```
Polish /to/[slug] to feel exactly like Typeform (PLAN.md §6, compare with screenshots):
- Framer Motion AnimatePresence transitions: slide+fade up on next, down on back (~350ms), direction-aware.
- Keyboard: Enter = OK/next (Shift+Enter newline in long text), ↑/↓ prev/next, letter keys A–Z select
  choices, Y/N for yes_no, digits for rating. Auto-focus the input on each question.
- Single-select auto-advance with a short blink animation on the selected option.
- Top progress bar (animated width) + bottom-right up/down chevron buttons + "press Enter ↵" hints.
- Error badge animation, mobile layout (sticky OK button on small screens), prefers-reduced-motion support.
- Accessible: proper labels, aria-live for errors, visible focus states.
```
✅ Done when: it genuinely feels like Typeform on desktop and mobile.

---

### Session 8 — Builder: drag-and-drop, live preview, publish & share (≈1.5 hr)
```
1. Drag-and-drop reorder of the sidebar question list with @dnd-kit/sortable (drag handle, drag overlay,
   keyboard sorting). Optimistic reorder, call PUT /questions/order, roll back + toast on failure.
2. Replace the centre canvas with the SHARED QuestionRenderer in 'preview' mode, wrapped in the form theme,
   with the question title, description and option labels editable inline on the canvas (contentEditable or
   auto-sizing inputs styled identically). Changes in the canvas and the settings panel stay in sync.
3. Preview button: opens a full-screen modal running the real respondent flow in preview mode (no submit to server).
4. Publish button: validates (show which questions block publishing), publishes, toast, then a
   "Your form is live" modal with the link + copy button. Publish button becomes "Published ✓" with an
   unpublish option in a menu.
5. /forms/[id]/share page: link, copy, open, QR-code-free simple layout, publish state.
```
✅ Done when: reorder persists, preview is pixel-identical to the live form.

---

### Session 9 — Results (≈1.5 hr)
```
Build /forms/[id]/results with sub-tabs Summary and Responses (see screenshots):
- Header stats: total responses, (completion rate placeholder until bonus), last response time.
- Summary: one card per question in order. Choice/dropdown/yes_no → horizontal bars with count + %;
  rating → average with star display + distribution bars; number → avg/min/max; text → latest answers list
  with "N responses". Build small reusable chart components (no heavy chart lib needed).
- Responses: table (date + one column per question, truncated cells, sticky header, horizontal scroll),
  pagination, click row → side drawer showing the full response in order, delete response with confirm.
- Empty state when no responses, with a "Share your form" CTA.
- "Download CSV" button hitting /responses.csv.
```
✅ Done when: seeded data shows meaningful summaries and table.

---

### Session 10 — Settings, placeholders, polish pass (≈1 hr)
```
- Theme settings panel in the builder (right panel tab "Design"): accent color, background color,
  question color, font (3–4 Google fonts) — saved to form.theme and applied in preview + live form.
- Thank-you screen settings (already editable — make sure it has its own panel in the same style).
- ComingSoon placeholders wired for: Logic jumps, Integrations/webhooks, Team/sharing, Payment and
  File upload question types (show them greyed-out in the Add Question modal with a "Soon" badge).
- Consistency pass over every screen against docs/screenshots: spacing, font sizes, hover states,
  focus rings, empty/loading/error states, toasts. Fix anything that looks generic.
- Remove dead code, ensure no TS `any`, lint and build clean.
```

---

### Session 11 — Bonuses (optional, pick what time allows)
Paste only the parts you want:
```
A) Partial responses + completion rate: create the response (status in_progress) when the respondent
   answers the first question, upsert answers as they advance (POST /public/forms/{slug}/responses/{rid}/answers),
   mark completed on submit. Show completion rate + drop-off per question on Summary. Responses table
   shows only completed by default with a toggle.
B) Dark mode for the creator app (class strategy, toggle in sidebar, persisted).
C) Basic branching: per choice/yes_no question, rules "if answer is X → jump to question Y / end".
   Store as JSON in questions.properties.logic, enforce in useFormRunner and progress calculation,
   validate server-side that skipped questions aren't required-checked.
D) File-upload question type: add 'file_upload' to the type enum (backend + frontend registry), a
   `file_uploads` table (id, answer_id FK cascade, original_name, stored_path, mime_type, size_bytes),
   POST /public/forms/{slug}/uploads (multipart, size + type limits, stored under UPLOAD_DIR with a
   random name) returning an upload id that the answer references; drag-and-drop upload renderer in
   the respondent flow; download link in the response drawer. Remove its "Soon" badge.
   Update PLAN.md §2 schema and README.
```

---

### Session 12 — Deploy + README (≈1 hr)
```
1. Backend deploy config (Railway with a volume, or Render with a persistent disk): start command,
   DATABASE_URL pointing at the mounted volume (the assignment requires all forms and responses to persist,
   so the SQLite file must NOT live on ephemeral storage), CORS_ORIGINS = the frontend URL,
   run seed on first boot only if the DB is empty.
2. Frontend on Vercel: NEXT_PUBLIC_API_URL = backend URL, NEXT_PUBLIC_APP_URL = Vercel URL.
   Verify in an incognito window: workspace loads, share link from the Share page opens /to/[slug],
   a submission appears in Results, and data survives a backend redeploy/restart.
3. Write README.md covering EVERY item the assignment asks for: overview + screenshots/GIF, live demo link,
   tech stack (and why FastAPI), setup instructions (backend + frontend + seed + env vars),
   architecture overview (with a simple diagram), database schema (PLAN.md §2 + ER diagram + design decisions),
   API overview table, assumptions (single default creator, SQLite, cascade on question delete, etc.),
   what's mocked / Coming soon, bonuses done, known limitations, note on AI tool usage.
4. Final audit: walk PLAN.md §0 top to bottom against the deployed app and report any row that is not
   fully working.
```
Note: check each host's current free-tier limits for persistent storage before choosing one.

✅ Done when: deployed link works in incognito, data persists across restarts, repo is public,
every row of §0 is ticked.

---

## 8. Interview prep (do after each session, 5 min)
Ask Claude Code: *"Explain what you built this session as if I'm being interviewed on it: the data flow,
the key decisions, and 3 likely questions with answers."* Save answers in `docs/notes.md`.

---

## 9. Submission checklist (assignment "Deliverables" + "Submission")
- [ ] Code pushed to GitHub; repository is **public**; contains `frontend/` and `backend/`
- [ ] README has setup instructions, tech stack, architecture overview, database schema, API overview, assumptions
- [ ] Seed data loaded on the deployed instance (≥2 published forms, mixed types, existing responses)
- [ ] Frontend deployed (Vercel) and backend deployed (Railway / Render) with persistent SQLite
- [ ] Public form link works without login in an incognito window and on a phone
- [ ] No `.env`, `.db` files or secrets committed
- [ ] Submitted **both** the GitHub repo link and the deployed app link before the deadline
- [ ] Re-read `docs/notes.md` before the evaluation interview

---

## Progress
- [x] Session 0 — Scaffolding
- [x] Session 1 — DB models + seed
- [ ] Session 2 — Creator API
- [ ] Session 3 — Public + results API
- [ ] Session 4 — Foundation + workspace
- [ ] Session 5 — Builder core
- [ ] Session 6 — Respondent core
- [ ] Session 7 — Respondent feel
- [ ] Session 8 — DnD, live preview, publish
- [ ] Session 9 — Results
- [ ] Session 10 — Settings + polish
- [ ] Session 11 — Bonuses
- [ ] Session 12 — Deploy + README
