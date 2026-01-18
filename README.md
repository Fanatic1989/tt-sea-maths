# TT SEA Maths Tutor (MVP, $0-friendly)

This repo is a **starter project** for:
- Trinidad & Tobago Primary Maths (STD 1–5)
- **SEA Study Simulator** (40 questions: Section I=20, II=16, III=4)
- Constructed-response only (no multiple choice)
- Strict learning loop (attempts → hints → examples → steps)

This is an MVP scaffold you can run **on a Chromebook** and deploy using **free tiers**.

## Folder structure

- `backend/` FastAPI API (question generation + checking)
- `frontend/` Next.js UI

## Quick start (local)

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Test:
- Open `http://localhost:8000/health` → `{"status":"ok"}`
- Open `http://localhost:8000/sea/paper` → JSON paper

### 2) Frontend

In a new terminal:

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_BASE=http://localhost:8000
npm run dev
```

Open:
- `http://localhost:3000`

## Deploy for $0

### Backend (Render free)
- Push to GitHub
- Create a Render "Web Service" from `backend/`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel free)
- Import the GitHub repo
- Project root: `frontend/`
- Add environment variable:
  - `NEXT_PUBLIC_API_BASE` = your Render backend URL

## Skillmap file

`backend/data/tt_primary_skillmap.json` currently contains a **minimal** skeleton.

As we build, we will replace it with the **full STD1–STD5 map** and use it to drive paper composition.

## What’s implemented right now

- SEA paper endpoint: `/sea/paper`
- Answer checker endpoint: `/answer/check`
- Attempt logging endpoint: `/attempt/log` (SQLite)
- A few working generators:
  - integer add/sub
  - simplify fractions
  - add/sub fractions (unlike denominators)
  - percent of quantity
  - elapsed time (returns answer like `H:MM`)

## Next steps (we’ll do step-by-step)

1) Replace skillmap with the full Trinidad STD1–STD5 list
2) Add generator functions for each skill type
3) Expand UI: true lock/unlock across navigation + results + weak-topic redo
4) Add curated YouTube links mapped by skill

