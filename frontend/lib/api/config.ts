/**
 * Public frontend configuration.
 *
 * Only NEXT_PUBLIC_* variables reach the browser. Backend secrets (Gemini
 * key, Google service-account) must never be placed here — the frontend
 * talks to FastAPI and never to Google Sheets directly.
 */
export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");
