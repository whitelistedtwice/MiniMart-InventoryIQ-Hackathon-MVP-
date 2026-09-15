# InventoryIQ Deployment Guide

Target architecture:

- **Frontend:** Vercel (Next.js)
- **Backend:** Render (Docker / FastAPI)
- **Data:** Google Sheets (read-only)
- **AI:** Google Gemini (optional)

## 1. Google Sheets setup

1. Create a Google Sheet with four tabs: **Products**, **Sales**, **Inventory**, **Shipments**.
2. Use the column names from `backend/demo/cambodian_mini_mart.json`.
3. In Google Cloud Console, create a service account with **Viewer** access to the sheet.
4. Download the service-account JSON key.

## 2. Backend deployment (Render)

1. Push code to GitHub.
2. In Render, create a new **Blueprint** from `render.yaml`, or manually create a **Web Service** using Docker with `backend/Dockerfile`.
3. Set environment variables in the Render dashboard:
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_SERVICE_ACCOUNT_JSON` (paste the full JSON string)
   - `CORS_ALLOW_ORIGINS` (your Vercel frontend URL, e.g. `https://inventoryiq.vercel.app`)
   - `GEMINI_API_KEY` (optional)
   - `GEMINI_MODEL` = `gemini-3.5-flash`
   - `BUSINESS_NAME`, `BUSINESS_TYPE`, `BUSINESS_CURRENCY` (e.g. `USD` or `KHR`)
4. Render health check uses `/health`.

## 3. Frontend deployment (Vercel)

1. Import the GitHub repo into Vercel.
2. Set **Root Directory** to `frontend`.
3. Add environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` = your Render backend URL (e.g. `https://inventoryiq-api.onrender.com`)
4. Deploy.

## 4. Demo mode (no Google credentials)

Set `DEMO_MODE=true` on the backend. The app loads `backend/demo/cambodian_mini_mart.json` instead of Google Sheets. The Settings page still shows **Not configured** for Sheets because demo mode does not claim a live connection.

## 5. Local vs production configuration

| Variable | Local | Production |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Render backend URL |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000` | Vercel frontend origin |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | optional; use file fallback | paste full JSON |
| `DEMO_MODE` | `true` for quick UI demo | `false` |

## 6. Security reminders

- Never commit `.env` files or service-account JSON.
- Frontend never receives Gemini keys or Google credentials.
- `sheets_connection_state` is a live probe; no fake "connected" status.
