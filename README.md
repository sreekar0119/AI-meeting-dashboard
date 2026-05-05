# AI Meeting Insights Dashboard

AI Meeting Insights Dashboard is a complete MVP for uploading meeting transcripts, generating structured insights, and tracking action items without using a database. The backend uses FastAPI with Pydantic validation and JSON-file persistence. The frontend uses React, Vite, TypeScript, and Tailwind for a responsive manager-friendly dashboard.

## Stack

- Frontend: React + Vite + TypeScript + Tailwind CSS
- Backend: FastAPI + Pydantic
- Storage: Local JSON files only
- Tests: Pytest + Vitest

## What is implemented

- Create meetings from transcript input
- Generate insights per meeting
- Deterministic mock insight extractor when `OPENAI_API_KEY` is not set
- Optional OpenAI-backed insight generation when `OPENAI_API_KEY` is set
- CRUD-ready action item API with dedicated status updates
- Meeting list filters by date range, participant, owner, and status
- Dashboard KPIs, recent meetings, overdue tasks
- Meeting detail page with transcript, summaries, decisions, blockers, and action items
- Action items table and kanban views with inline status changes
- Safe JSON writes using temp files plus atomic replace
- File locking to prevent concurrent write corruption
- Seed data with 5 meetings and 15 action items

## Project tree

```text
project/
├── README.md
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       ├── action_items.py
│   │   │       ├── dashboard.py
│   │   │       ├── health.py
│   │   │       └── meetings.py
│   │   ├── repositories/
│   │   │   ├── contracts.py
│   │   │   ├── json_action_item_repository.py
│   │   │   ├── json_insight_repository.py
│   │   │   └── json_meeting_repository.py
│   │   ├── services/
│   │   │   ├── action_items.py
│   │   │   ├── container.py
│   │   │   ├── dashboard.py
│   │   │   ├── insights.py
│   │   │   └── meetings.py
│   │   ├── utils/
│   │   │   ├── file_lock.py
│   │   │   ├── ids.py
│   │   │   └── json_store.py
│   │   ├── config.py
│   │   ├── errors.py
│   │   ├── main.py
│   │   └── schemas.py
│   ├── data/
│   │   ├── action_items.json
│   │   ├── insights.json
│   │   └── meetings.json
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_action_items.py
│   │   ├── test_insights.py
│   │   └── test_meetings.py
│   ├── .env.example
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/
    │   │   ├── client.ts
    │   │   └── types.ts
    │   ├── components/
    │   │   ├── ActionItemKanban.tsx
    │   │   ├── ActionItemTable.tsx
    │   │   ├── AppShell.tsx
    │   │   ├── Card.tsx
    │   │   ├── EmptyState.tsx
    │   │   ├── ErrorState.tsx
    │   │   ├── KpiCard.tsx
    │   │   ├── LoadingState.tsx
    │   │   ├── MeetingCard.tsx
    │   │   ├── PriorityBadge.tsx
    │   │   └── StatusBadge.tsx
    │   ├── hooks/
    │   │   └── useAsyncData.ts
    │   ├── pages/
    │   │   ├── ActionItemsPage.tsx
    │   │   ├── DashboardPage.tsx
    │   │   ├── MeetingDetailPage.tsx
    │   │   └── MeetingUploadPage.tsx
    │   ├── test/
    │   │   ├── action-items.test.tsx
    │   │   ├── dashboard.test.tsx
    │   │   └── setup.ts
    │   ├── utils/
    │   │   └── format.ts
    │   ├── App.tsx
    │   ├── index.css
    │   └── main.tsx
    ├── .env.example
    ├── index.html
    ├── package.json
    ├── postcss.config.cjs
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── tsconfig.node.json
    └── vite.config.ts
```

## Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend base URL:

```text
http://127.0.0.1:8000/api
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend base URL:

```text
http://127.0.0.1:5173
```

## Environment variables

Backend `.env.example`

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
FRONTEND_ORIGIN=http://localhost:5173
APP_DATA_DIR=backend/data
```

Frontend `.env.example`

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Test commands

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## API summary

- `GET /api/health`
- `GET /api/dashboard`
- `POST /api/meetings`
- `GET /api/meetings`
- `GET /api/meetings/{meeting_id}`
- `DELETE /api/meetings/{meeting_id}`
- `GET /api/meetings/{meeting_id}/insights`
- `POST /api/meetings/{meeting_id}/insights`
- `GET /api/action-items`
- `POST /api/action-items`
- `GET /api/action-items/{item_id}`
- `PATCH /api/action-items/{item_id}`
- `PATCH /api/action-items/{item_id}/status`
- `DELETE /api/action-items/{item_id}`

## Data files

The app persists records in these JSON files:

- `backend/data/meetings.json`
- `backend/data/action_items.json`
- `backend/data/insights.json`

Each write is protected by:

- A lock file handled in `backend/app/utils/file_lock.py`
- Atomic temp-file replacement in `backend/app/utils/json_store.py`

## Demo script: 2 to 3 minutes

1. Open the dashboard at `http://localhost:5173`.
2. Point out seeded KPIs, recent meetings, and overdue follow-ups.
3. Open one recent meeting and show the transcript, short summary, detailed summary, decisions, blockers, and generated action items.
4. Go to `New Meeting`, paste a transcript, and submit.
5. Show that the app saves the meeting, generates insights automatically, and lands on the meeting detail page.
6. Open `Action Items`, filter by the new meeting, and move one task from `Open` to `In Progress` or `Complete`.
7. Return to the dashboard and explain that all persistence is backed only by local JSON files with safe writes and locking.

## Verification status

- Backend tests passed with `pytest`
- Frontend tests passed with `npm test`
- Frontend production build passed with `npm run build`
