# InventoryIQ — Concerns & Project Reminders

Living project-health log. Every concern is verified against the actual
repository before being recorded. Update before each phase; do not delete
entries without resolution, acceptance, deferral, or out-of-scope reasoning.

Statuses: `OPEN` `INVESTIGATING` `DEFERRED` `RESOLVED` `ACCEPTED / KNOWN LIMITATION` `OUT OF SCOPE`
Severities: `CRITICAL` `HIGH` `MEDIUM` `LOW`

---

## C-001 Google Sheets write capability unverified

- Severity: HIGH
- Status: OUT OF SCOPE
- Area: Google Sheets / stock adjustment
- Discovered: Phase 9
- Description: Phase 2 verified READ only. `GOOGLE_SHEET_ID` and
  `GOOGLE_SERVICE_ACCOUNT_FILE` are absent from the local environment and no
  service-account JSON exists in the repo, so the safe write/read/restore
  preflight could not be performed. The write path is entirely unimplemented
  in code (`app/data_access/sheets.py` has no write functions), though gspread
  6.2.1 natively supports cell updates. The current MVP does NOT implement
  manual stock adjustment or any Google Sheets write-back, so write
  capability is not required.
- Required resolution: none for the current MVP. If write-back is ever
  approved, obtain an Editor service account, add a single write seam, and run
  the safe preflight (update one test cell → read back → verify Shipments
  untouched → restore → read back).
- Owner: None (out of MVP scope; re-open only with explicit approval)
- Verification: frontend negative-scope scan shows no Adjust Stock or
  write-back UI (Phase 11).

## C-002 `sheets_connected` is environment-presence only

- Severity: MEDIUM
- Status: OPEN
- Area: Settings / API
- Discovered: Phase 8, confirmed Phase 9
- Description: `GET /api/v1/settings` reports `sheets_connected: true` when
  `GOOGLE_SHEET_ID` and `GOOGLE_SERVICE_ACCOUNT_FILE` env vars exist — it has
  never attempted connectivity. Truthful states are required:
  `Not Configured`, `Configured`, `Connected / Verified`, `Connection Error`.
- Required resolution: introduce a connection-state model (additive contract
  change + frontend type sync), probe real connectivity for `Connected`.
- Owner: Phase 15
- Verification: settings response shows `Connection Error` with bad
  credentials and `Connected / Verified` with real credentials.

## C-003 Gemini default model was unavailable

- Severity: HIGH
- Status: RESOLVED
- Area: Gemini integration
- Discovered: Phase 9
- Description: The hard-coded default model `gemini-2.0-flash` returns
  `404 NOT_FOUND — "no longer available"` for the current account key.
  `gemini-2.5-flash` is also unavailable to new users. The live model list was
  queried; `gemini-3.5-flash` exists and works.
- Required resolution: resolved by changing `_DEFAULT_MODEL` to
  `gemini-3.5-flash` (verified live). `GEMINI_MODEL` env overrides remain.
- Owner: Phase 9 (done)
- Verification: `GET /v1beta/models` list (200) + live `generateContent` 200.

## C-004 Gemini transient 503 "high demand"

- Severity: MEDIUM
- Status: ACCEPTED / KNOWN LIMITATION
- Area: Gemini integration / demo reliability
- Discovered: Phase 9
- Description: `gemini-3.5-flash` intermittently returns
  `503 UNAVAILABLE — high demand` (observed twice in preflight). The
  integration degrades gracefully (`ai_available: false`, HTTP 200, no
  fabricated text); one attempt, no retries.
- Required resolution: none for MVP. If live-demo flakiness appears, consider
  exactly one bounded retry on 503/timeout (Phase 19 decision), never an
  aggressive loop.
- Owner: Phase 19
- Verification: failure-injection tests in `tests/test_gemini.py`; live
  observation recorded here.

## C-005 Gemini timeout too tight for real latency

- Severity: HIGH
- Status: RESOLVED
- Area: Gemini integration
- Discovered: Phase 9
- Description: The 15s timeout caused spurious failures: a successful live
  `gemini-3.5-flash` structured-output call took ~18.4s.
- Required resolution: resolved by raising `_TIMEOUT_SECONDS` to 45s. Smoke
  test then passed end-to-end through `explain_recommendation`.
- Owner: Phase 9 (done)
- Verification: live smoke test PASS (`ai_available: true`, structured fields
  parsed, deterministic quantity echoed unchanged).

## C-006 Deployment: service-account file path not host-friendly

- Severity: HIGH
- Status: OPEN
- Area: Deployment
- Discovered: Phase 9
- Description: `app/data_access/sheets.py` reads credentials from a FILE path
  (`GOOGLE_SERVICE_ACCOUNT_FILE`). PaaS hosts (Render/Railway/Fly/Vercel
  functions) provide secrets as env strings, not files. Backend also targets
  Python 3.14 locally; host runtime availability must be confirmed (3.13 is
  the widely supported stable).
- Required resolution: at deploy time, accept credentials as a base64 env var
  decoded to a temp file (no code change), or extend the loader to accept an
  inline JSON string (small code change). Confirm host Python runtime.
- Owner: Phase 20
- Verification: deployed backend reads Sheets successfully with env-provided
  credentials.

## C-007 Dashboard counts UNAVAILABLE products as healthy

- Severity: MEDIUM
- Status: OPEN
- Area: Dashboard / API contract
- Discovered: Phase 6, re-confirmed Phase 11
- Description: `build_business_brief_context` counts every non-actionable
  product — including `UNAVAILABLE` — as `healthy_items`. Phase 11 evidence:
  with all inventory snapshots removed, the Dashboard rendered
  "Need Attention 0 / Healthy 12" even though every product's stock was
  unknown (while `total_inventory_value` correctly showed "—"). The Dashboard
  displays backend truth verbatim; it cannot distinguish the two without a
  contract change.
- Required resolution: additive backend contract change: `unavailable_items`
  on `DashboardSummary`/`AIBusinessBriefContext`; brief stops counting
  UNAVAILABLE as healthy; frontend types and health card synced.
- Owner: Not scheduled — backend contract change (the presentation-only
  Phase 11 cannot resolve it; requires explicit approval per the
  no-silent-contract-change rule).
- Verification: dashboard with one UNAVAILABLE product shows
  `unavailable_items: 1` and excludes it from `healthy_items`.

## C-008 Repeated Google Sheets reads per logical operation

- Severity: LOW
- Status: ACCEPTED / KNOWN LIMITATION
- Area: API orchestration / performance
- Discovered: Phase 8, confirmed Phase 9
- Description: Each request calls `analyze(raw)` once and `read_sheets()` once
  per request — but dashboard + AI-brief + inventory + analytics are separate
  requests, so a full page load re-reads Sheets several times. Within one
  request, all outputs derive from a single consistent read (good).
- Required resolution: none for MVP. If latency hurts the demo, introduce a
  short-lived in-process snapshot (no Redis/DB) keyed per read, or a single
  server-side snapshot per refresh.
- Owner: Phase 16 (decision), Phase 20 (if latency observed in deployment)
- Verification: timing of demo page loads; request-count observation.

## C-009 "profit" field must be labeled Estimated Profit

- Severity: LOW
- Status: OPEN
- Area: Analytics UI / financial labeling
- Discovered: Phase 9
- Description: `FinancialMetrics.profit` is sales×price − sales×cost (gross
  only; no rent/salaries/tax). The backend field name is fine; only UI wording
  must not imply net profit.
- Required resolution: frontend label "Estimated Profit" (or "Estimated Gross
  Profit") everywhere the field is displayed. No contract change.
- Owner: Phase 14
- Verification: UI text review in Phase 18 visual QA.

## C-010 Business Health has no invented score (keep it that way)

- Severity: MEDIUM
- Status: RESOLVED
- Area: Dashboard
- Discovered: Phase 9, resolved Phase 11
- Description: Phase 11 implemented transparent indicators only: "Need
  Attention" (`items_needing_attention`), "Healthy" (`healthy_items`), and
  "Total Inventory Value" (`total_inventory_value`, with null shown as "—").
  No score, percentage, or grade is displayed or calculated.
- Required resolution: resolved by the Phase 11 Dashboard implementation.
- Owner: Phase 11 (done)
- Verification: Dashboard source and rendered screenshots (desktop, mobile,
  empty, missing-data); no score string exists in the dashboard code.

## C-011 Demo dataset exists but is not yet loaded into a real Sheet

- Severity: MEDIUM
- Status: OPEN
- Area: Demo data
- Discovered: Phase 9
- Description: `backend/demo/cambodian_mini_mart.json` provides 12 realistic
  products (Khmer+English names, USD prices, 14 days of sales, varied
  scenarios: healthy, stockout, excess, shipments, zero-demand-ish slow
  mover, missing lead time). It passes the full validation pipeline
  (5 tests). It is not yet in an actual Google Sheet, so no end-to-end demo
  against real Sheets is possible yet (also blocked by C-001).
- Required resolution: create the demo Google Sheet, paste/upload the four
  tabs, connect credentials, verify via `/api/v1/dashboard`.
- Owner: Phase 16 (integration), depends on C-001 (Phase 13)
- Verification: live dashboard/analytics responses against the real sheet.

## C-012 Shipment arriving TODAY — semantics locked

- Severity: MEDIUM
- Status: RESOLVED
- Area: Analytics / recommendation semantics
- Discovered: Phase 9 (audit of Phase 4/5 behavior)
- Description: Locked definition, already consistent across layers: a
  shipment with `expected_arrival == as_of` IS counted as incoming
  (`expected_arrival >= as_of` filter), `days_until_arrival == 0`, and
  `stockout_before_arrival` is False (`days_left < 0` is never true), so it
  counts toward expected stock and prevents REORDER. This is intentional:
  an arrival-today shipment is available for today's planning.
- Required resolution: none — semantics already consistent across layers and
  intentionally locked. Re-verify only if shipment logic changes.
- Owner: Phase 9 (documented). Re-verify if shipment logic changes.
- Verification: `test_shipment_arriving_today` (Phase 5 suite) +
  `_shipment` filter inspection.

## C-013 Manual stock adjustment semantics — decision locked

- Severity: HIGH
- Status: OUT OF SCOPE
- Area: Stock adjustment
- Discovered: Phase 9
- Description: The current MVP explicitly does NOT support manual stock
  adjustment or Inventory → Google Sheets write-back, and the frontend must
  not represent it. If scope is ever approved to change, the locked semantics
  are: update the product's latest inventory snapshot row in place (date
  unchanged) so the Phase 3 duplicate `(product_id, date)` rule is never
  triggered; append a new row dated today only when the product has no
  snapshots; never touch Shipments; then refresh (re-read → recalculate).
  Zero stock is valid; negative is rejected by validation.
- Required resolution: none for the current MVP. Re-open only with explicit
  scope approval; implement using a verified write seam (see C-001).
- Owner: None (out of MVP scope)
- Verification: frontend negative-scope scan shows no Adjust Stock or stock
  editing UI (Phase 11).

## C-014 Business Profile persistence — decision locked

- Severity: LOW
- Status: OPEN (decision made; implementation pending)
- Area: Settings (Phase 15)
- Discovered: Phase 9
- Description: No persistence exists; `business_name`/`business_type` are
  always null. Decision: single business, so persist via env vars
  (`BUSINESS_NAME`, `BUSINESS_TYPE`) — zero infrastructure. A new optional
  `Settings` tab in the demo Sheet is the fallback if UI editing is later
  required (not planned).
- Required resolution: implement env-var persistence (`BUSINESS_NAME`,
  `BUSINESS_TYPE`) in Phase 15; no database.
- Owner: Phase 15
- Verification: settings response reflects configured env values; no DB.

## C-015 Frontend API client / base-URL configuration

- Severity: MEDIUM
- Status: RESOLVED
- Area: Frontend foundation
- Discovered: Phase 9, resolved Phase 10
- Description: Phase 9 found no fetch/API code and no base-URL config in
  `frontend/`. Phase 10 added `lib/api/config.ts`
  (`NEXT_PUBLIC_API_BASE_URL`, dev default `http://localhost:8000`),
  `lib/api/client.ts` (network/server/invalid error taxonomy, never surfaces
  raw backend messages), and `lib/api/routes.ts` (existing endpoint paths).
  Pages do not consume it yet — that is intentional; feature pages arrive in
  Phases 11+.
- Required resolution: resolved in Phase 10. Later phases must use this client
  (and call `/api/v1/ai/*` separately/lazily) rather than fetching directly.
- Owner: Phase 10 (done)
- Verification: production build + type check pass; no secret appears in the
  built client bundle; placeholder routes render.

## C-016 Gemini is architecturally lazy — keep it that way

- Severity: LOW
- Status: ACCEPTED / KNOWN LIMITATION
- Area: AI loading
- Discovered: Phase 9
- Description: AI outputs live on separate endpoints (`/api/v1/ai/*`);
  deterministic endpoints never call Gemini. Dashboard returns the brief
  CONTEXT, not generated text. The frontend (Phase 10+) must call `/ai/*`
  separately so core data loads without AI latency.
- Required resolution: none for MVP — frontend must call `/api/v1/ai/*`
  separately (Phase 10/11); never inline AI into deterministic endpoints.
- Owner: Phase 10/11 (must consume lazily)
- Verification: network behavior — dashboard loads before AI brief renders.

## C-017 Priority ordering tie-breaker — locked

- Severity: MEDIUM
- Status: RESOLVED
- Area: Recommendation / dashboard ordering
- Discovered: Phase 9
- Description: Locked rule: all priority-ordered lists sort by
  `(priority, product_id)` — lower priority value first, then stable
  product_id. Used by `build_business_brief_context`, `build_insight_context`,
  and the dashboard `top_priorities`. Deterministic; no dictionary/UI-order
  dependence.
- Required resolution: none — rule already implemented and tested at every
  ordering site; reuse `(priority, product_id)` for any new ordered list.
- Owner: Phase 9 (documented)
- Verification: `test_business_brief_counts_and_ordering` +
  `test_insight_context_trends_and_highlights`.

## C-018 Request timestamps use server-local time

- Severity: LOW
- Status: ACCEPTED / KNOWN LIMITATION
- Area: API / date semantics
- Discovered: Phase 9
- Description: `generated_at` fields use `datetime.now()` (server local).
  They are cosmetic (display only) and never feed business decisions;
  business `as_of` now uses `business_today()` (Asia/Phnom_Penh, C-019).
- Required resolution: none for MVP; optionally use business-tz-aware
  timestamps if the frontend displays them prominently.
- Owner: Phase 12 (if displayed)
- Verification: code review; no business logic reads generated_at.

## C-019 Business `as_of` used server-local date (now fixed)

- Severity: HIGH
- Status: RESOLVED
- Area: Analytics / date semantics
- Discovered: Phase 9
- Description: `compute_product_analytics` defaulted to `date.today()`
  (server timezone). On a UTC server, shipment inclusion/`as_of` semantics
  could differ from the Phnom Penh business day by up to 7 hours.
- Required resolution: resolved — added `app/core/clock.py`
  (`business_today()`, Asia/Phnom_Penh) used as the `as_of` default.
- Owner: Phase 9 (done)
- Verification: `tests/test_clock.py` (3 tests) incl. UTC-vs-+7 boundary and
  engine-default wiring.

## C-020 CORS configuration for production

- Severity: LOW
- Status: OPEN
- Area: Deployment / security
- Discovered: Phase 9
- Description: Local CORS verified live (allowed origin receives
  `access-control-allow-origin`, disallowed origin receives nothing,
  preflight OK, methods GET/OPTIONS only). Production origins must be set via
  `CORS_ALLOW_ORIGINS` at deploy time; defaults only cover localhost.
- Required resolution: set `CORS_ALLOW_ORIGINS` to the deployed frontend
  origin(s) at deploy time.
- Owner: Phase 20
- Verification: deployed frontend fetches deployed backend without CORS
  errors.

## C-021 Sheets read failures surface as 502 with upstream message

- Severity: LOW
- Status: ACCEPTED / KNOWN LIMITATION
- Area: Error handling
- Discovered: Phase 9
- Description: `DataAccessError` messages embed the upstream exception text
  (e.g. gspread errors). No stack traces or secrets leak (verified), but
  messages can be verbose. Acceptable for MVP debugging; sanitize if
  user-facing polish is needed.
- Required resolution: none for MVP — acceptable for debugging; sanitize
  upstream text in error messages if user-facing polish is needed.
- Owner: Phase 19 (final security/reliability audit)
- Verification: error envelope inspection (already in Phase 8 tests).

## C-022 Top-bar controls are presentational only

- Severity: LOW
- Status: RESOLVED
- Area: Frontend shell / UX
- Discovered: Phase 10
- Description: The shared top bar originally rendered the reference's search
  field with no behaviour. Phase 12 resolved this: there is exactly ONE
  product-search implementation (the Inventory page), and the top-bar
  GlobalSearch submits into it — it navigates to `/inventory?q=…`, and the
  Inventory page adopts the query through `useSearchParams` into its own
  search state. No duplicate independent search state, no global fuzzy
  search, no cross-entity search, and no search/notification backend
  endpoint exist. The bell remains decorative (no notification system in the
  MVP).
- Required resolution: resolved in Phase 12.
- Owner: Phase 12 (done)
- Verification: `frontend/tests/inventory.spec.ts` —
  "global search routes the query into the inventory list search" asserts
  top-bar search → `/inventory?q=angkor` → page search holds the same query
  and filters the list; "a late AI response from product A cannot overwrite
  product B AI insight" and the list tests confirm no second search control
  fires or exists.

## C-023 No currency is provided by the backend

- Severity: LOW
- Status: OPEN
- Area: Dashboard / Analytics / API contract
- Discovered: Phase 11
- Description: Financial values (e.g. `total_inventory_value`) have no
  currency in any contract, so the Dashboard shows e.g. "1,180.05" without a
  symbol. During Phase 11 verification, Gemini's brief independently wrote
  "$1,180.05" — the AI inferred a currency the deterministic layer never
  stated. The Settings UI spec expects a currency field "when supported";
  C-014 plans env-based business profile in Phase 15.
- Required resolution: add currency to the business profile/configuration
  (Phase 15, with C-014) and expose it to the frontend; format financial
  values consistently from that value.
- Owner: Phase 15
- Verification: financial values display the configured currency; no
  hardcoded currency symbol exists in the frontend.
