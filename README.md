# InventoryIQ

An inventory intelligence tool for **Cambodian mini-mart owners**. It turns
existing sales and inventory data into simple, practical restocking
decisions — helping owners avoid stockouts and excess stock.

## Tech stack

- **Frontend:** React / Next.js + Tailwind CSS
- **Backend:** Python + FastAPI
- **Data processing:** Pandas

## Running the frontend

```
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Running the backend

```
cd backend
py -V:3.14 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn main:app --reload --port 8000
```

Health check: http://localhost:8000/health

## Development plan

Development proceeds in phases (see `InventoryIQ_TEAM_PROMPT_PLAN_FINAL.md`
and `InventoryIQ_SOURCE_OF_TRUTH.md`). This repository is currently at
**Phase 0 — environment initialization only**. No product features have
been implemented yet.
