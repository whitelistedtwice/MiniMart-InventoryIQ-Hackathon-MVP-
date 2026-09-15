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

## C-002 `sheets_connection_state` is a cached live probe

- Severity: MEDIUM
- Status: RESOLVED
- Area: Settings / API
- Discovered: Phase 8, resolved Phase 16
- Description: `GET /api/v1/settings` now returns `sheets_connection_state`
  (`not_configured`, `configured`, `connected`, `error`) from a cached live
  probe of Google Sheets. `sheets_connected` remains for compatibility and is
  `True` only when the probe succeeds. Demo mode correctly reports
  `not_configured` because it does not use Sheets.
- Required resolution: implemented in Phase 16.
- Owner: Phase 16 (done)
- Verification: tests in `tests/test_api.py` and `tests/test_data_access.py`
  assert `not_configured`, `error`, and `connected` states; manual server
  verification shows dashboard/settings return quickly in demo mode.

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

## C-006 Deployment: service-account credentials as env string

- Severity: HIGH
- Status: RESOLVED
- Area: Deployment
- Discovered: Phase 9, resolved Phase 16
- Description: `app/data_access/sheets.py` now accepts
  `GOOGLE_SERVICE_ACCOUNT_JSON` (raw JSON string) in addition to
  `GOOGLE_SERVICE_ACCOUNT_FILE`. A `backend/Dockerfile` (Python 3.13 slim)
  and `render.yaml` provide a Render deployment path. `requirements.txt`
  was converted from UTF-16LE to UTF-8 so pip inside Docker can parse it.
- Required resolution: implemented in Phase 16.
- Owner: Phase 16 (done)
- Verification: tests assert JSON env credential loading; Dockerfile and
  render.yaml are present and reference the correct paths/variables.

## C-007 Dashboard counts UNAVAILABLE products separately

- Severity: MEDIUM
- Status: RESOLVED
- Area: Dashboard / API contract
- Discovered: Phase 6, resolved Phase 16
- Description: `DashboardSummary` and `AIBusinessBriefContext` now include
  `unavailable_items`. The backend counts only `NO ACTION` products as
  `healthy_items`; `UNAVAILABLE` products are counted separately. The
  frontend `BusinessHealth` card displays the new "Unavailable" count.
- Required resolution: implemented in Phase 16.
- Owner: Phase 16 (done)
- Verification: `test_business_brief_unavailable_items_are_counted_separately`
  and the demo-mode dashboard test assert the correct split
  (8 attention, 3 healthy, 1 unavailable for the demo dataset).

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

## C-009 "profit" field is labeled Estimated Profit

- Severity: LOW
- Status: RESOLVED
- Area: Analytics UI / financial labeling
- Discovered: Phase 9, resolved Phase 16
- Description: The Analytics page labels the financial column
  "Estimated Profit" and its explainer says "estimated gross profit".
- Required resolution: implemented in Phase 16.
- Owner: Phase 16 (done)
- Verification: UI text review in `frontend/app/(app)/analytics/page.tsx`.

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
  products and passes the full validation pipeline. Phase 16 added
  `DEMO_MODE=true`, which loads this JSON directly so the app is demoable
  without a real Sheet. A real Google Sheet with the same tabs is still not
  created.
- Required resolution: create the demo Google Sheet and connect credentials
  to verify the live pipeline end-to-end. Demo mode mitigates this for
  hackathon demos.
- Owner: Phase 16+ (integration), depends on C-001 (out of scope)
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

## C-014 Business Profile persistence via environment

- Severity: LOW
- Status: RESOLVED
- Area: Settings (Phase 15/16)
- Discovered: Phase 9
- Description: `BUSINESS_NAME`, `BUSINESS_TYPE`, and `BUSINESS_CURRENCY`
  are read from environment variables by `app/core/business.py`. No
  database, account system, or write path exists.
- Required resolution: implemented.
- Owner: Phase 15/16 (done)
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
- Status: RESOLVED
- Area: Deployment / security
- Discovered: Phase 9
- Description: `main.py` reads allowed origins from `CORS_ALLOW_ORIGINS`.
  `render.yaml` declares it as a manual env var and `docs/DEPLOYMENT.md`
  instructs setting it to the deployed frontend origin.
- Required resolution: set `CORS_ALLOW_ORIGINS` at deploy time.
- Owner: Phase 16 (done)
- Verification: deployed frontend fetches deployed backend without CORS
  errors (to be confirmed after actual deployment).

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

## C-023 Currency is provided by the backend and used everywhere

- Severity: LOW
- Status: RESOLVED
- Area: Dashboard / Analytics / API contract
- Discovered: Phase 11
- Description: `business_currency()` reads `BUSINESS_CURRENCY` from env and
  the backend passes it through SettingsResponse and all AI contexts. The
  frontend `formatMoney` uses the configured currency and falls back to
  plain amounts when unset. Gemini is instructed not to invent a currency.
- Required resolution: implemented in Phase 15/16.
- Owner: Phase 15/16 (done)
- Verification: financial values display the configured currency; no
  hardcoded currency symbol exists in frontend source.
