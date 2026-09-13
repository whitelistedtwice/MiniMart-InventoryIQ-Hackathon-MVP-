# InventoryIQ Architecture & Contracts

This document describes the internal structure and contracts established in
**Phase 1**. It is the implementation guide that later phases must follow.

The authoritative product specification remains
`InventoryIQ_SOURCE_OF_TRUTH.md`.

------------------------------------------------------------------------

## 1. Overall architecture

InventoryIQ is a layered backend with a thin frontend display layer.

``` text
Google Sheets (Phase 2: gspread, read-only)
        ↓
Data Access (app/data_access)
        ↓
Validation (app/validation)
        ↓
Processing (app/processing)
        ↓
Analytics Engine (app/analytics)
        ↓
Recommendation Engine (app/recommendations)
        ↓
Verified AI Context (app/ai_context)
        ↓
Gemini Client (app/gemini)
        ↓
FastAPI Routes (app/api/routes)
        ↓
React / Next.js Frontend
```

### Golden rules

1. **Backend owns business logic.** The frontend never recomputes core
   metrics or recommendations.
2. **Gemini explains verified results.** It never calculates, overrides,
   or invents business data.
3. **Missing data is not zero.** Optional/null fields mean "unavailable".
4. **Current inventory and incoming shipments stay separate.**

------------------------------------------------------------------------

## 2. Directory structure

``` text
backend/
├── app/
│   ├── contracts/           # Pydantic data models (shared across layers)
│   │   ├── data.py          # Products, Sales, Inventory, Shipments
│   │   ├── analytics.py     # Demand, inventory, shipment, financial metrics
│   │   ├── recommendation.py
│   │   ├── ai_context.py
│   │   └── api.py           # API response models
│   ├── core/
│   │   └── errors.py        # Shared exception hierarchy
│   ├── data_access/         # Google Sheets reads (Phase 2)
│   ├── validation/          # Raw-data validation (Phase 3)
│   ├── processing/          # Normalize + join data (Phase 3)
│   ├── analytics/           # Deterministic calculations (Phase 4)
│   ├── recommendations/     # Deterministic actions (Phase 5)
│   ├── ai_context/          # Verified context builder (Phase 6)
│   ├── gemini/              # Gemini API client (Phase 7)
│   └── api/
│       └── routes/          # FastAPI endpoints (Phase 8+)
│           ├── dashboard.py
│           ├── inventory.py
│           ├── analytics.py
│           ├── settings.py
│           └── ai.py
├── tests/                   # Architecture + API contract tests
├── main.py                  # FastAPI app factory
└── requirements.txt

frontend/
└── app/
    └── types.ts             # TypeScript mirror of backend contracts
```

------------------------------------------------------------------------

## 3. Data flow

1. **Read:** Google Sheets → raw dictionaries.
2. **Validate:** required sheets/columns, dates, numbers, IDs, duplicates.
3. **Process:** group records by product into `ProcessedProduct` objects.
4. **Analyze:** compute demand, inventory, shipment, and financial metrics.
5. **Recommend:** produce a deterministic `RecommendationResult`.
6. **Build AI context:** copy verified analytics/recommendation values into
   a structure that Gemini is allowed to see.
7. **Explain (optional):** Gemini turns the verified context into plain
   language. If Gemini fails, the deterministic data still returns.
8. **Respond:** FastAPI serializes deterministic data + AI explanation into
   the documented response shapes.

------------------------------------------------------------------------

## 4. Core data contracts

Defined in `backend/app/contracts/data.py`.

### Product

- `product_id`
- `product_name` (supports Khmer, English, mixed)
- `category`
- `unit`
- `unit_cost`
- `selling_price`
- `supplier`
- `lead_time_days`
- `target_stock_days`

### Sale

- `date`
- `product_id`
- `quantity_sold`

### InventorySnapshot

- `date`
- `product_id`
- `quantity_on_hand`

> A missing snapshot is represented by the **absence** of a record, not by
> `quantity_on_hand = 0`.

### Shipment

- `shipment_id`
- `product_id`
- `quantity`
- `expected_arrival`

> Shipments are **never** merged into current inventory.

------------------------------------------------------------------------

## 5. Analytics contract

Defined in `backend/app/contracts/analytics.py`.

`ProductAnalytics` groups:

- `DemandMetrics`: total_sold, average_daily_sales, recent_daily_sales,
  trend (`increasing` | `stable` | `decreasing` | `unavailable`)
- `InventoryMetrics`: current_stock, inventory_value,
  days_of_stock_remaining, stock_status, stockout_risk
- `ShipmentProjection`: incoming_quantity, expected_arrival,
  days_until_arrival, expected_future_inventory, stockout_before_arrival
- `FinancialMetrics`: revenue, estimated_cost, profit, profit_margin,
  financial_exposure

Every numeric field is optional. `None` means **unavailable**, not zero.

------------------------------------------------------------------------

## 6. Recommendation contract

Defined in `backend/app/contracts/recommendation.py`.

Supported actions:

| Action            | Meaning                                  |
|-------------------|------------------------------------------|
| `REORDER`         | Stockout risk; reorder now               |
| `REDUCE EXCESS`   | Materially excessive/slow-moving stock   |
| `MONITOR / PREPARE` | Developing trend; no immediate action  |
| `NO ACTION`       | Healthy                                  |
| `UNAVAILABLE`     | Insufficient data for a reliable call    |

Priority order (lower number = higher priority):

1. `UNAVAILABLE`
2. `REORDER`
3. `REDUCE EXCESS`
4. `MONITOR / PREPARE`
5. `NO ACTION`

`RecommendationResult` carries:

- `action` and `priority`
- `reorder_quantity` (when REORDER)
- `reorder_timing`
- `incoming_stock_sufficient`
- `evidence` list

The exact formulas belong to **Phase 5**.

------------------------------------------------------------------------

## 7. Verified AI context contract

Defined in `backend/app/contracts/ai_context.py`.

Gemini receives only:

- `AIProductContext` (per-product verified facts)
- `AIBusinessBriefContext` (dashboard summary)
- `AIRecommendationContext` (product-detail explanation input)
- `AIInsightContext` (analytics-page insight input)

Rules:

- All numbers come from analytics/recommendation results.
- Missing values are explicit (`None`).
- No raw spreadsheet rows are sent.
- Gemini cannot alter the `recommendation_action` or `reorder_quantity`.

------------------------------------------------------------------------

## 8. API response conventions

Defined in `backend/app/contracts/api.py`.

Routes use `response_model=...` so FastAPI validates outgoing JSON.

Key responses:

- `GET /api/v1/dashboard` → `DashboardResponse`
- `GET /api/v1/inventory` → `list[ProductListItem]`
- `GET /api/v1/inventory/{product_id}` → `ProductDetailResponse`
- `GET /api/v1/analytics` → `AnalyticsResponse`
- `GET /api/v1/settings` → `SettingsResponse`
- `GET /api/v1/ai/business-brief` → `AIExplanationResponse`
- `GET /api/v1/ai/recommendation/{product_id}` → `AIExplanationResponse`
- `GET /api/v1/ai/insight` → `AIExplanationResponse`

Errors are returned as `ApiError`:

``` json
{
  "error": "validation_error",
  "message": "Missing required column",
  "details": {}
}
```

------------------------------------------------------------------------

## 9. Important invariants / guardrails

1. **Missing inventory ≠ 0 inventory.** Use `Optional[int]` with `None`
   for unavailable values.
2. **Current stock and incoming shipments are separate.** Never overwrite
   `current_stock` with shipment quantity.
3. **Frontend does not calculate.** It only renders backend-provided
   numbers.
4. **Gemini is an explanation layer.** It receives verified context and
   returns plain language; it does not own the truth.
5. **Gemini failure is graceful.** Deterministic endpoints still return
   analytics and recommendations even when AI explanation is unavailable.
6. **Errors carry codes.** Each layer raises a specific subclass of
   `InventoryIQError` so the API can return predictable error envelopes.

------------------------------------------------------------------------

## 10. Phase responsibilities

| Phase | Responsibility | Where it lives |
|-------|----------------|----------------|
| 0 | Toolchain + repo setup | (done) |
| 1 | Architecture + contracts | `app/contracts`, `app/core`, `docs/ARCHITECTURE.md` |
| 2 | Google Sheets data access | `app/data_access/sheets.py` |
| 3 | Validation + processing + fixtures | `app/validation/`, `app/processing/`, `tests/fixtures/` |
| 4 | Deterministic analytics | `app/analytics/engine.py` |
| 5 | Recommendation engine | `app/recommendations/engine.py` |
| 6 | Verified AI context builder | `app/ai_context/builder.py` |
| 7 | Gemini integration | `app/gemini/client.py` |
| 8 | FastAPI routes | `app/api/routes/` |
| 9 | Figma/MCP workflow test | (outside product code) |
| 10 | Frontend shell + components | `frontend/app/` |
| 11 | Dashboard page | `frontend/app/dashboard/` |
| 12 | Inventory + Product Detail | `frontend/app/inventory/` |
| 13 | Manual stock adjustment | API route + sheet write |
| 14 | Analytics page | `frontend/app/analytics/` |
| 15 | Settings + Sheets connection UI | `frontend/app/settings/` |
| 16+ | Integration, testing, polish | Across both stacks |

------------------------------------------------------------------------

## 11. What is NOT in this phase

No business logic, no Google Sheets API, no Gemini API, no dashboard UI,
no analytics UI, no settings UI, no authentication, no payments, no POS,
no supplier ordering.

Phase 1 stops here.
