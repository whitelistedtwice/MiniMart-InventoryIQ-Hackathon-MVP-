# InventoryIQ --- Team Prompt Plan

**Project:** InventoryIQ\
**Purpose:** Phase-by-phase implementation plan for OpenCode\
**Authoritative specification:** `InventoryIQ_SOURCE_OF_TRUTH.md`

> This document tells the team **what to prompt OpenCode at each
> stage**. The Source of Truth defines what InventoryIQ is; this
> document defines the order and discipline for building it.

------------------------------------------------------------------------

# How To Use This Plan

Build InventoryIQ **one phase at a time**.

For each phase:

1.  OpenCode reads `InventoryIQ_SOURCE_OF_TRUTH.md`.
2.  Send the phase prompt exactly or with only minor contextual changes.
3.  OpenCode implements only that phase.
4.  Run the required tests/checks.
5.  Review the result.
6.  Fix issues before moving on.
7.  Commit the phase when it is verified.
8.  Move to the next phase.

## Global Rule For OpenCode

At the start of every phase:

> Read `InventoryIQ_SOURCE_OF_TRUTH.md` before making changes. Treat it
> as the authoritative source of truth. Do not revive, invent, or
> silently add features outside its MVP scope.

If a requirement is genuinely ambiguous and would materially affect
architecture or business logic, **stop and ask for clarification rather
than guessing**.

------------------------------------------------------------------------

# Phase 0 --- Initialize the Agent, Repository, and Toolchain

## Goal

Before writing product code, make OpenCode understand exactly what it is
building and prepare the development environment.

This phase is about **initialization only**.

## Prompt To Send OpenCode

``` text
You are the primary coding agent for InventoryIQ.

Before writing application code, initialize this project properly.

1. Read `InventoryIQ_SOURCE_OF_TRUTH.md` completely and treat it as the authoritative source of truth.
2. Summarize your understanding of:
   - target user
   - problem
   - solution
   - MVP scope
   - non-MVP/future scope
   - data model
   - deterministic recommendation architecture
   - Gemini's role
   - website structure
   - technical stack
3. Explicitly confirm that the MVP is ONLY for Cambodian mini-mart owners.
4. Explicitly confirm that the MVP does NOT include food/restaurant functionality, ingredients, recipes, menu items, supplier ordering, payments, subscriptions, POS integrations, or dynamic arbitrary spreadsheet interpretation.
5. Inspect the current repository and environment before creating files.
6. Determine whether this is a new project or an existing project and preserve useful existing work only if it clearly belongs to this InventoryIQ project.
7. Set up the agreed stack:
   - Frontend: React / Next.js
   - Styling: Tailwind CSS
   - Backend: Python + FastAPI
   - Data processing: Pandas
   - Data source: Google Sheets
   - AI: Gemini API
8. Inspect the available OpenCode/MCP/tooling environment.
9. Identify the tools/plugins/integrations actually required for:
   - Google Sheets access
   - Gemini API access
   - frontend/backend development
   - testing
   - Figma/MCP later
10. Do not install unnecessary tools or services.
11. Configure environment-variable handling safely. Never hard-code API keys or credentials.
12. Set up:
   - formatting
   - linting
   - testing
   - dependency management
   - basic development scripts
   - `.gitignore`
   - `.env.example`
13. Establish a clean repository structure suitable for the layered architecture in the Source of Truth.
14. Create a minimal health/smoke test proving the frontend and backend toolchain can run.
15. Do NOT implement InventoryIQ features yet.

At the end, report:
- repository structure
- tools/plugins available and which are actually needed
- dependencies installed
- environment variables required
- commands to run frontend/backend/tests
- anything that could block the next phase

Stop after initialization and verification.
```

## Exit Criteria

-   Project runs locally.
-   Frontend toolchain works.
-   Backend toolchain works.
-   Tests execute.
-   Environment secrets are safely configured.
-   Required tools are understood.
-   No unnecessary product features have been implemented.

**Review gate:** Do not continue until the environment is healthy.

------------------------------------------------------------------------

# Phase 1 --- Project Architecture and Contracts

## Goal

Create the clean application structure and define stable internal
contracts before implementing business logic.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Now implement Phase 1 only: establish the project architecture and internal contracts.

Create a clean layered structure for:

1. Google Sheets/data source access
2. Validation
3. Data processing
4. Analytics
5. Recommendation engine
6. Verified AI context
7. Gemini integration
8. API layer
9. Frontend

Define typed/structured contracts between these layers.

Important:
- Backend owns business logic.
- Frontend must not calculate core business metrics.
- Gemini must receive verified structured context.
- Missing data must remain distinguishable from zero.
- Current inventory and incoming shipments must remain separate.

Create minimal placeholder interfaces where necessary, but do not implement full analytics yet.

Add architecture-level tests for the most important contracts.

Do not build the dashboard, analytics UI, or Gemini features yet.
Do not add features outside the Source of Truth.

Run lint/type checks/tests and report results.
```

## Exit Criteria

-   Layer boundaries exist.
-   Contracts are explicit.
-   No business logic is duplicated in the frontend.
-   Tests pass.

------------------------------------------------------------------------

# Phase 2 --- Google Sheets Data Access

## Goal

Build the MVP's data-source layer.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 2 only: Google Sheets data access.

Implement a reliable way for the backend to read the four required sheets:

- Products
- Sales
- Inventory
- Shipments

Respect the exact MVP schemas in the Source of Truth.

Requirements:
- Use environment variables/secrets safely.
- Do not hard-code credentials.
- Keep Google Sheets access isolated from analysis logic.
- Return structured data suitable for validation.
- Handle connection/read failures cleanly.
- Do not silently substitute fake business data when the real source fails.
- Keep shipment data separate from inventory data.

Create tests using mocked Google Sheets responses so the test suite does not depend on a live external account.

Do not implement analytics or recommendations yet.

Run all tests and report failures clearly.
```

## Exit Criteria

-   Google Sheets layer works against mocks.
-   Connection failures are handled.
-   Data is returned in predictable structures.
-   No credentials are committed.

------------------------------------------------------------------------

# Phase 3 --- Validation and Data Processing

## Goal

Turn raw Google Sheets data into clean, validated, analysis-ready data.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 3 only: validation and data processing.

Validate:
- required sheets
- required columns
- dates
- numeric values
- product IDs
- duplicates where inappropriate
- shipment dates
- required product fields

Normalize supported data into analysis-ready structures.

Critical rules:
- Missing inventory is NOT zero.
- Do not invent missing values.
- Do not silently delete invalid business records.
- Clearly report validation problems.
- Preserve Khmer, English, and mixed Khmer/English product names.
- Keep current inventory and incoming shipments separate.

Add unit tests for valid data and invalid/edge cases.

Create a small deterministic fixture dataset for tests.

Also establish the project's **canonical business-scenario fixtures**. These are small, named scenarios that will be reused throughout analytics, recommendation, API, and end-to-end testing rather than each phase inventing different examples.

At minimum include:
- Healthy product
- Immediate stockout risk
- Shipment arriving before projected stockout
- Shipment arriving after projected stockout
- Excess/slow-moving product
- Increasing-demand product

Each fixture should document its important inputs and expected high-level outcome.

Do not implement recommendations, Gemini, or UI.
```

## Exit Criteria

-   Valid data reaches the next layer.
-   Invalid data produces useful errors/warnings.
-   Missing data semantics are tested.

------------------------------------------------------------------------

# Phase 4 --- Deterministic Demand and Inventory Analytics

## Goal

Implement the core business calculations.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 4 only: deterministic analytics.

Implement:
1. Total units sold
2. Average daily sales
3. Recent demand
4. Demand trend:
   - Increasing
   - Stable
   - Decreasing
5. Current stock
6. Inventory value
7. Days of stock remaining
8. Incoming quantity
9. Days until shipment
10. Expected future inventory
11. Stockout-related measurements
12. Excess inventory measurements
13. Revenue
14. Estimated cost
15. Profit
16. Profit margin
17. Financial exposure
18. Simple future preparation signal

Use only the simple MVP methodology described by the Source of Truth.

Do NOT add:
- advanced forecasting
- complex seasonality
- complex statistics
- weighted risk scores
- scenario simulation

Important:
- Missing data must not become fabricated values.
- Missing inventory is not zero.
- Zero-demand cases must not crash.
- Zero/invalid denominators must be handled safely.
- Financial metrics must be unavailable when required inputs are missing.
- Current inventory and incoming shipment quantities must remain separate.

Keep all calculations in the backend.

Write strong unit tests for normal and edge cases.

Do not build the UI yet.
```

## Exit Criteria

-   Core metrics are deterministic and tested.
-   Edge cases do not crash.
-   No advanced statistics have been introduced.

------------------------------------------------------------------------

# Phase 5 --- Recommendation Engine

## Goal

Turn verified analytics into clear business actions.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 5 only: the deterministic recommendation engine.

Supported actions are exactly:

- REORDER
- REDUCE EXCESS
- MONITOR / PREPARE
- NO ACTION
- UNAVAILABLE

Implement the priority order:

1. UNAVAILABLE
2. Stockout / REORDER
3. EXCESS
4. FUTURE PREPARATION
5. MONITOR
6. NO ACTION

The engine must consider:
- current stock
- demand
- lead time
- target stock coverage
- incoming shipment quantity
- incoming shipment timing

Implement:
- recommendation action
- recommended reorder quantity
- reorder timing
- whether incoming stock is sufficient
- evidence/reasons

Use the conceptual reorder relationship from the Source of Truth:

Recommended reorder quantity
= Desired stock - Expected available stock

Define the exact MVP formula explicitly in code/documentation and test it.

Important:
- The frontend must not calculate this.
- Gemini must not calculate or override it.
- Avoid unreachable/dead conflict logic.
- Do not invent missing values.
- Return UNAVAILABLE where reliable recommendation is impossible.

Create tests using the canonical business-scenario fixtures:
- healthy product
- immediate stockout
- shipment before stockout
- shipment after stockout
- excess stock
- increasing demand

Also test:
- zero demand
- missing inventory
- insufficient history
- missing shipment
- missing lead time
- conflicting signals

Do not implement Gemini or frontend yet.
```

## Exit Criteria

-   Recommendation behavior is deterministic.
-   Exact formulas are documented.
-   Business scenarios make sense.
-   Tests cover recommendation conflicts and edge cases.

**Review gate:** Manually inspect several recommendation examples before
continuing.

------------------------------------------------------------------------

# Phase 6 --- Verified AI Context Layer

## Goal

Create the exact structured context that Gemini will receive.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 6 only: the verified AI context layer.

Create a structured context object that is produced ONLY from validated backend analysis and recommendation results.

The context may include fields such as:
- business information
- product identity
- current stock
- demand
- days remaining
- demand trend
- shipment quantity
- shipment timing
- risk
- recommendation
- reorder quantity
- evidence/reasons
- inventory value
- excess information where relevant

Rules:
- Never calculate new business metrics inside the AI context layer.
- Never invent missing values.
- Do not send unnecessary raw spreadsheet data.
- Do not allow Gemini to alter the recommendation.
- Make unavailable fields explicit.

Write tests proving that context is consistent with backend results.

Do not call Gemini yet.
Do not build UI yet.
```

## Exit Criteria

-   Gemini has a clean, verified contract.
-   Context values exactly match backend truth.

------------------------------------------------------------------------

# Phase 7 --- Gemini Integration

## Goal

Connect Gemini safely as an explanation layer.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 7 only: Gemini integration.

Gemini's role is:
- explain recommendations
- summarize business conditions
- explain trends
- highlight priorities
- give simple contextual advice based ONLY on verified context

Gemini must NOT:
- calculate core metrics
- invent numbers
- invent missing data
- invent shipments
- override recommendations
- assume unavailable information

Implement the structured AI response requested by the Source of Truth:

- summary
- reason
- action_explanation
- future_note

Requirements:
- Use environment variables for API credentials.
- Handle timeout, rate limit, invalid response, unavailable API, and malformed output.
- Validate the AI response before returning it.
- Never let Gemini failure break deterministic functionality.
- Provide a deterministic fallback state.

Write mocked tests for:
- successful Gemini response
- malformed response
- API failure
- timeout
- unavailable key
- contradictory/unsafe AI output

Do not build the frontend AI cards yet.
```

## Exit Criteria

-   Gemini works through a clean service layer.
-   Failure is graceful.
-   AI cannot override deterministic truth.

------------------------------------------------------------------------

# Phase 8 --- Backend API

## Goal

Expose the complete verified backend to the frontend.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 8 only: FastAPI API layer.

Expose the data required by the MVP frontend.

At minimum, create API capabilities for:
- health check
- dashboard overview
- product list
- product detail
- analytics
- Google Sheets refresh/read state
- manual stock adjustment
- AI Business Brief
- AI product recommendation explanation
- AI analytics insight

Use structured response models.

Important:
- Frontend receives backend truth.
- Do not expose raw internal objects unnecessarily.
- Do not make the frontend reconstruct core business logic.
- Recommendation results must already contain their calculated action/evidence.
- AI endpoints must use verified context.
- Gemini failure should return a graceful AI-unavailable state while deterministic data remains available.

Add API tests for normal and error cases.

Do not build the real frontend screens yet.
```

## Exit Criteria

-   API endpoints are stable.
-   Response contracts are documented/tested.
-   Frontend can consume deterministic and AI results.

------------------------------------------------------------------------

# Phase 9 --- Figma → MCP Tiny Test

## Goal

Test whether the chosen Figma-to-OpenCode workflow is reliable enough
before building the real UI.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Do NOT implement the actual InventoryIQ frontend yet.

We are performing a tiny Figma-to-code workflow test.

Use the simple Figma test design provided by the team.

Goal:
Figma
→ Figma MCP
→ OpenCode
→ localhost

Implement ONLY the tiny test screen.

Do not build the full InventoryIQ navigation, dashboard, analytics, inventory, or settings.

After implementation:
1. Run the test locally.
2. Compare the localhost result against the Figma design.
3. Report:
   - layout fidelity
   - typography fidelity
   - spacing
   - components
   - responsiveness
   - ease of making changes
   - MCP/tool reliability

Do not redesign the test unnecessarily.

Stop after the evaluation.
```

## Decision Gate

### If good

Use Figma MCP for the real UI.

### If mediocre

Use Figma MCP + screenshots + explicit implementation instructions.

### If unreliable

Use Figma screenshots/design specs directly.

**Do not allow the MCP workflow to dictate the application
architecture.**

------------------------------------------------------------------------

# Phase 10 --- Frontend Foundation

## Goal

Build the real frontend shell after the Figma workflow decision.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Now begin the real InventoryIQ frontend.

Implement Phase 10 only: frontend foundation.

Create:
- application shell
- routing/navigation
- reusable layout
- reusable cards
- status badges
- buttons
- tables
- charts foundation
- loading states
- error states
- empty states
- API client
- typed frontend data models

Use the final Figma workflow decided in Phase 9.

Important:
- Do not invent new product pages.
- Do not implement business calculations in React.
- Keep components reusable.
- Keep mini-mart-specific terminology.
- Prepare the UI for Khmer/English/mixed product names.
- Make AI states explicit.
- Keep deterministic and AI outputs visually distinguishable.

Do not implement the complete dashboard or analytics yet.
```

## Exit Criteria

-   Frontend shell works.
-   API connection works.
-   Reusable components exist.
-   No business logic has leaked into UI.

------------------------------------------------------------------------

# Phase 11 --- Dashboard

## Goal

Build the primary owner-facing dashboard.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 11 only: Dashboard.

The Dashboard must include exactly the MVP dashboard features:

1. Business Health
2. Top Priorities
3. AI Business Brief (GEMINI)
4. Historical Overview
5. Refresh/update state where appropriate

The dashboard should answer:
- What is happening?
- What needs attention?
- What should I look at first?

Top priorities should link to product detail.

AI Business Brief:
- use backend verified context
- explain the most important business conditions
- do not independently calculate metrics
- gracefully show AI unavailable if Gemini fails

Keep the dashboard clean and action-oriented.
Do not add unrelated charts or features.
```

## Exit Criteria

-   Dashboard matches the approved design.
-   Real API data renders.
-   Priority clicks work.
-   AI failure does not break dashboard.

------------------------------------------------------------------------

# Phase 12 --- Inventory + Product Detail

## Goal

Build the main inventory workflow.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 12 only: Inventory page and Product Detail.

Inventory page:
- Product List
- Search
- Simple filters
- Current stock
- Status
- Days remaining
- Relevant action
- Product selection/navigation

Product Detail:
- Current Stock
- Demand
- Days Remaining
- Inventory Value
- Incoming Shipments
- Recommendation
- Evidence / Reasons
- Historical Trend
- Manual Stock Adjustment
- See What AI Recommends (GEMINI)

AI interaction:
The deterministic recommendation must appear first.

Example:
🔴 REORDER
Recommended: 24 units
[ ✨ See What AI Recommends ]

Clicking the control expands the Gemini explanation.

Important:
- Do not recalculate recommendation values in the frontend.
- Keep current inventory and incoming shipment separate.
- Product switching must clear/update product-specific state correctly.
- Handle missing data and unavailable recommendations.
- Long product names and Khmer/English names must render correctly.

Do not implement Analytics or Settings in this phase.
```

## Exit Criteria

-   Product list works.
-   Product detail works.
-   Search/filter works.
-   AI expansion works.
-   Manual adjustment UI exists and connects to backend.
-   No stale product state.

------------------------------------------------------------------------

# Phase 13 --- Manual Stock Adjustment Backend Integration

## Goal

Verify the stock adjustment workflow end-to-end.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement/finish Phase 13: manual stock adjustment integration.

The workflow must be:

Inventory
→ Adjust Stock
→ Update current physical inventory
→ Google Sheets Inventory
→ Refresh
→ Recalculate analysis

Important:
- This must update current inventory only.
- It must NOT overwrite or consume shipment records.
- Current stock and incoming shipment remain separate.
- Validate the adjustment before writing.
- Handle Google Sheets write failure safely.
- Do not claim success if the write failed.

Add tests for:
- valid adjustment
- invalid quantity
- product not found
- Google Sheets failure
- shipment remaining unchanged
- refreshed analysis reflecting the adjustment

Do not add unrelated editing features.
```

## Exit Criteria

-   Adjustment works end-to-end.
-   Shipment records remain untouched.
-   Failure states are trustworthy.

------------------------------------------------------------------------

# Phase 14 --- Analytics Page

## Goal

Build the deeper business-analysis page.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 14 only: Analytics page.

Include:

Demand
- Total sales
- Average sales
- Recent sales
- Demand trend

Inventory
- Stock levels
- Days remaining
- Inventory value
- Stock status

Financial
- Revenue
- Estimated cost
- Profit
- Profit margin

Historical Trends
- Sales/demand over time
- Inventory over time
- Useful demand/inventory comparison where supported

AI Insight (GEMINI)
- small AI card
- explain meaningful verified trends
- no independent calculations
- graceful AI failure

Keep analytics readable and useful for a mini-mart owner.

Do not introduce advanced statistics, forecasting, scenario simulation, or new analytics categories.
```

## Exit Criteria

-   All required analytics are visible.
-   Charts use backend data.
-   AI insight uses verified context.
-   No scope expansion.

------------------------------------------------------------------------

# Phase 15 --- Settings + Google Sheets Connection UI

## Goal

Finish the lightweight Settings area.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 15 only: Settings.

Settings should contain:

1. Business Profile
   - Business name
   - Business type
   - Basic required business information

2. Google Sheets Connection
   - Connect/load
   - Connection state
   - Refresh/reconnect
   - Last update/sync information where available

Keep this page lightweight.

Do not add:
- subscription settings
- payment settings
- supplier marketplace
- multi-location management
- complex account/team management

Ensure connection errors are understandable.

Run frontend and API tests.
```

## Exit Criteria

-   Settings works.
-   Google Sheets state is visible.
-   No future features have leaked into MVP.

------------------------------------------------------------------------

# Phase 16 --- Full End-to-End Integration

## Goal

Connect every layer into one working product.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Implement Phase 16: complete end-to-end integration.

Verify the real flow:

Google Sheets
→ Validation
→ Data Processing
→ Analytics
→ Recommendation Engine
→ Verified AI Context
→ Gemini
→ API
→ Frontend

Verify these user journeys:

1. Load data
2. Open Dashboard
3. See Business Health
4. See Top Priorities
5. Open a product
6. Inspect recommendation/evidence
7. Expand "See What AI Recommends"
8. View Analytics
9. View AI Insight
10. Adjust current stock
11. Refresh
12. See updated results

Remove placeholder data from production paths.

Verify that the frontend does not silently use stale/mock values.

Verify that Gemini failure leaves deterministic functionality usable.

Do not add new product features.
```

## Exit Criteria

The entire MVP works from data source to UI.

**Major review gate:** Manually test the complete owner journey before
continuing.

------------------------------------------------------------------------

# Phase 17 --- Comprehensive Testing + Business Logic Audit

## Goal

Find problems that normal happy-path tests may miss, while reusing the same canonical business scenarios established earlier.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Perform a full testing and business-correctness audit.

Do not add new features.

Test:
- healthy product
- stockout
- excess inventory
- shipment before stockout
- shipment after projected stockout
- increasing demand
- decreasing demand
- stable demand
- zero demand
- missing inventory
- missing sales
- missing shipment
- missing lead time
- missing cost/price
- invalid dates
- invalid numbers
- negative inventory
- duplicate product/date
- insufficient history
- empty data
- single product
- multiple products/categories
- Khmer names
- English names
- mixed Khmer/English names

Audit specifically:
- missing inventory is never treated as zero
- current stock and shipment stock remain separate
- reorder quantity is backend-owned
- frontend does not recreate business calculations
- Gemini cannot override recommendations
- missing information becomes unavailable where appropriate
- Gemini failure does not break the product
- invalid calculations do not crash
- no recommendation logic is unreachable/dead
- financial metrics are not fabricated

Test both unit and integration behavior.

Fix genuine defects found in the current MVP.

Do not introduce new scope.
```

## Exit Criteria

-   Core test suite passes.
-   Business behavior is manually reviewed.
-   Known edge cases are covered.

------------------------------------------------------------------------

# Phase 18 --- Visual QA and UX Audit

## Goal

Make the MVP presentation-ready without changing its scope.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Perform a visual and UX audit of the complete InventoryIQ MVP.

Do not add new features.

Review:
- Dashboard
- Inventory list
- Product Detail
- Analytics
- Settings
- AI Business Brief
- AI Recommendation expansion
- AI Insight
- Loading states
- Error states
- Empty states
- Google Sheets connection states
- Manual adjustment states

Check:
- visual hierarchy
- spacing
- alignment
- typography
- readability
- responsive behavior
- chart clarity
- status colors/labels
- AI visibility
- recommendation visibility
- long product names
- Khmer/English text
- stale state after product switching
- broken components
- visible HTML/CSS artifacts
- confusing buttons
- inconsistent terminology

Use the approved Figma design as reference.

Fix only issues that improve correctness, usability, or visual quality without expanding product scope.
```

## Exit Criteria

-   No obvious visual defects.
-   User journey is clear.
-   AI features are easy to discover.
-   Recommendations are visually prominent.
-   UI feels like a real mini-mart product.

------------------------------------------------------------------------

# Phase 19 --- Final Security / Reliability / Scope Audit

## Goal

Prepare the MVP for demonstration and prevent accidental scope creep.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Perform the final InventoryIQ MVP audit.

Check:

1. Scope
- Only MVP features are implemented.
- No future feature has accidentally become required functionality.
- No supplier marketplace/order system.
- No payments/subscriptions.
- No POS integration.
- No dynamic arbitrary spreadsheet interpretation.
- No unrelated business modes.

2. Security
- No API keys committed.
- No credentials hard-coded.
- `.env` is ignored.
- `.env.example` contains placeholders only.
- External API failures are handled safely.

3. Reliability
- Startup works from a clean environment.
- Frontend starts.
- Backend starts.
- Tests run.
- Google Sheets errors are handled.
- Gemini errors are handled.
- Empty/malformed data is handled.

4. Architecture
- Backend owns business logic.
- Frontend displays backend truth.
- Gemini receives verified context.
- Data layers remain separated.

5. UX
- Dashboard immediately communicates priorities.
- Product recommendations are clear.
- AI features are discoverable.
- Manual stock adjustment is understandable.

Fix only genuine issues.

Do not add features.
```

## Exit Criteria

-   MVP is stable.
-   Secrets are safe.
-   Scope is clean.
-   Demo can start reliably.

------------------------------------------------------------------------

# Phase 20 --- Demo Preparation and Final Documentation

## Goal

Prepare the project for the hackathon/demo without changing the product.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Prepare InventoryIQ for a live demo.

Do not add new product features.

Create/finish:
- README with setup instructions
- environment setup instructions
- Google Sheets test-data instructions
- local development commands
- test commands
- architecture overview
- concise explanation of deterministic logic vs Gemini
- demo-ready sample mini-mart data if needed

Ensure the demo dataset clearly demonstrates:
1. a stockout/reorder case
2. an excess-stock case
3. an incoming shipment timing case
4. an increasing-demand case
5. healthy products

Make the demo flow reliable and easy to reproduce.

Do not build supplier ordering, subscriptions, payments, or future features.
```

## Exit Criteria

A teammate can clone/setup/run the project and reproduce the demo.

------------------------------------------------------------------------

# Phase 21 --- Final Git / Release Check

## Goal

Create a clean final state.

## Prompt

``` text
Read `InventoryIQ_SOURCE_OF_TRUTH.md`.

Perform a final release check.

Do not change product scope.

1. Run the complete test suite.
2. Run lint/type checks.
3. Verify frontend build.
4. Verify backend startup.
5. Verify environment configuration.
6. Check for accidental secrets.
7. Check for dead/unused code introduced during development.
8. Check for debug prints and temporary test UI.
9. Check for placeholder data in production paths.
10. Check README/setup instructions.
11. Check git diff and repository status.
12. Summarize all remaining known limitations.

Only after everything is clean, prepare the repository for the final commit.

Do not implement future roadmap features.
```

## Exit Criteria

-   Final tests pass.
-   Build passes.
-   No secrets.
-   No accidental placeholder paths.
-   Repository is clean and demo-ready.

------------------------------------------------------------------------

# Global Review Gates

Do not blindly move phase-to-phase.

## Gate A --- After Phase 0

Ask:

> Can OpenCode reliably build and test the project?

If no, fix tooling first.

## Gate B --- After Phase 5

Ask:

> Do the recommendations make business sense?

Manually inspect real mini-mart scenarios before adding AI/UI.

## Gate C --- After Phase 7

Ask:

> Does Gemini explain deterministic truth without becoming the source of
> truth?

If no, fix the AI contract.

## Gate D --- After Phase 9

Ask:

> Is Figma → MCP → OpenCode reliable enough?

Choose MCP, MCP + screenshots, or screenshots/specs.

## Gate E --- After Phase 16

Ask:

> Can a mini-mart owner complete the entire core workflow?

If no, do not move to polish.

## Gate F --- After Phase 18

Ask:

> Would we be comfortable showing this UI to a judge or real mini-mart
> owner?

If no, polish existing functionality rather than adding features.

------------------------------------------------------------------------

# OpenCode Rules To Repeat When Necessary

Use these rules whenever OpenCode starts drifting:

``` text
1. Read the Source of Truth.
2. Build only the current phase.
3. Do not silently expand scope.
4. Backend owns business logic.
5. Frontend displays backend truth.
6. Missing data is not zero.
7. Never invent data.
8. Current inventory ≠ incoming shipment.
9. Gemini explains verified results; it does not determine them.
10. Gemini failure must not break deterministic functionality.
11. Test real integration paths, not just isolated functions.
12. Do visual QA.
13. Stop and ask when an architectural/business requirement is genuinely ambiguous.
```

------------------------------------------------------------------------

# Phase Dependency Map

``` text
Phase 0
  ↓
Phase 1
  ↓
Phase 2
  ↓
Phase 3
  ↓
Phase 4
  ↓
Phase 5
  ↓
Phase 6
  ↓
Phase 7
  ↓
Phase 8
  ↓
Phase 9 ──→ Figma/MCP decision
  ↓
Phase 10
  ↓
Phase 11
  ↓
Phase 12
  ↓
Phase 13
  ↓
Phase 14
  ↓
Phase 15
  ↓
Phase 16
  ↓
Phase 17
  ↓
Phase 18
  ↓
Phase 19
  ↓
Phase 20
  ↓
Phase 21
```

------------------------------------------------------------------------

# Final Build Philosophy

The team should not try to make InventoryIQ impressive by making it
huge.

The MVP should be impressive because the **core loop works extremely
well**:

``` text
Mini-Mart Data
      ↓
InventoryIQ
      ↓
What is happening?
      ↓
What needs attention?
      ↓
What should I do?
      ↓
Why?
      ↓
Gemini explains
      ↓
Owner acts
```

**Build the smallest reliable product that proves this loop.**

Anything outside the MVP belongs in the future roadmap, not in the
implementation.
