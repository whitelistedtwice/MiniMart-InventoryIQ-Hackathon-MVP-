# InventoryIQ (MiniMart)


An inventory intelligence tool for **Cambodian mini-mart owners**. It turns
existing sales and inventory data into simple, practical restocking
decisions — helping owners avoid stockouts and excess stock.

## Tech stack

- **Frontend:** React / Next.js + Tailwind CSS
- **Backend:** Python + FastAPI
- **Data source:** Google Sheets (read-only)
- **AI explanations:** Google Gemini (optional)

## Running locally

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your Google Sheets and Gemini credentials
py -V:3.14 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn main:app --reload --port 8000
```

Health check: http://localhost:8000/health

### Frontend

```bash
cd frontend
cp .env.example .env.local
# Edit .env.local to point at the backend (default: http://localhost:8000)
npm install
npm run dev
```

Open http://localhost:3000

## Architecture

See `docs/ARCHITECTURE.md` for the project structure, data flow, and the
contracts that the frontend and backend share.

## Deployment

See `docs/DEPLOYMENT.md` for Vercel + Render deployment instructions,
environment variables, Google Sheets service-account setup, and demo mode.
