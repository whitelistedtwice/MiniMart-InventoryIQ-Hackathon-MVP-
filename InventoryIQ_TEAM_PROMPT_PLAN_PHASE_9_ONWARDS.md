# InventoryIQ — Team Prompt Plan (Phase 9 Onwards)

> Continuation of the InventoryIQ team execution plan after Phases 0–8.
> Use this together with `InventoryIQ_SOURCE_OF_TRUTH.md`, the existing architecture/contracts, and `docs/CONCERNS.md`.

---

# 1. How to Use This Plan

Every phase follows:

```text
Read Source of Truth
→ Read Architecture / API contracts
→ Read docs/CONCERNS.md
→ Read current phase
→ Implement only approved scope
→ Test
→ Audit
→ Update concerns
→ Report evidence
→ STOP for human review
→ whitelist commits/pushes manually
```

The agent must NOT automatically commit, push, or merge.

Every phase must contain:

- Goal
- Scope
- What NOT to Change
- Implementation Requirements
- Tests
- Verification
- Reporting
- Exit Criteria

---

# 2. Project-Wide Rules

## 2.1 Source-of-truth hierarchy

When sources conflict:

1. `InventoryIQ_SOURCE_OF_TRUTH.md`
2. Backend contracts, architecture, and OpenAPI
3. Written UI/phase specifications
4. Visual reference images

Visual references define appearance, not business truth.

Reference-image numbers are placeholders and must never become hardcoded production data.

## 2.2 Living concern tracking

Maintain:

```text
docs/CONCERNS.md
```

This is the project's living **Current Concerns & Project Reminders** log.

Before every phase, read it.

When a material concern is discovered, add/update it with:

- ID
- severity
- status
- affected area
- discovered phase
- description
- required resolution
- owner/future phase
- verification method

Statuses:

```text
🔴 OPEN
🟠 INVESTIGATING
🟡 DEFERRED
🟢 RESOLVED
⚪ ACCEPTED / KNOWN LIMITATION
❌ OUT OF SCOPE
```

Severity:

```text
CRITICAL
HIGH
MEDIUM
LOW
```

Do not delete concerns simply because they are inconvenient. A concern is closed only after resolution, explicit acceptance, deferral, or out-of-scope classification with appropriate reasoning.

Track material concerns involving correctness, data integrity, business logic, security, reliability, UX, architecture, external dependencies, demo reliability, or scope. Do not fill this file with trivial lint warnings.

## 2.3 No silent contract changes

If an API/data/frontend contract needs to change:

1. Explain why.
2. Identify dependents.
3. Update the relevant contract.
4. Update tests.
5. Verify downstream compatibility.
6. Report the change.
7. Update `docs/CONCERNS.md` if material.

Never silently alter contracts to make implementation easier.

## 2.4 Regression protection

Every phase must rerun tests relevant to its changes.

Backend changes must preserve the existing backend test suite.

Frontend changes must preserve the frontend build/type checks and relevant tests.

Never accept a new feature that breaks previously verified business logic.

## 2.5 External dependency preflight

Before depending on an external service, API, account, package, hosting provider, MCP server, or platform capability, verify it in the actual environment.

Use:

```text
DEPENDENCY CHECK

Dependency:
Available:
Authenticated:
Actually working:
Plan/usage limitation:
Cost:
Fallback:
BLOCKING:
```

Documentation alone does not prove that the user's current plan/account/environment supports something.

## 2.6 MVP vs production vs demo

InventoryIQ is a hackathon MVP.

Explicitly distinguish:

- required MVP behavior
- intentional non-production limitations
- behavior that must be reliable for the live demo

Do not introduce authentication, multi-tenancy, databases, Redis, queues, microservices, complex caching, elaborate permissions, or similar infrastructure unless a demonstrated MVP requirement justifies it.

## 2.7 Single-business MVP

The MVP represents:

```text
one Cambodian mini-mart
one connected Google Sheet
```

Do not introduce multi-tenant architecture or organization/account systems without explicit approval.

## 2.8 No premature optimization

Prefer simple, correct, testable, understandable MVP solutions.

Do not introduce complex infrastructure for hypothetical scale.

## 2.9 No AI-driven scope creep

Gemini is an explanation/insight layer.

It must not become:

- the source of business truth
- the recommendation engine
- an autonomous ordering agent
- a giant chatbot
- a replacement for deterministic analytics
- a replacement for deterministic recommendations

No agentic AI features without explicit approval.

## 2.10 Human approval gate

Every phase ends:

```text
Agent implements
→ Agent tests
→ Agent audits
→ Agent reports
→ whitelist reviews
→ whitelist commits/pushes
```

---

# 3. Backend Rules

Existing architecture:

```text
Google Sheets
→ Data Access
→ Validation
→ Processing
→ Analytics
→ Recommendations
→ Verified AI Context
→ Gemini
→ FastAPI
→ Next.js
```

## 3.1 Missing is not zero

Missing data remains unavailable.

Never silently convert missing inventory, sales, shipment, cost, price, lead time, or other required information into zero/false.

## 3.2 Current inventory != incoming shipments

Example:

```text
Current stock = 15
Incoming shipment = 50
```

Do not represent current stock as 65.

Shipment timing affects projected availability and reorder logic.

## 3.3 Backend owns business calculations

Frontend must not independently calculate:

- days remaining
- inventory value
- revenue
- estimated profit
- margin
- trend
- stockout risk
- excess
- reorder quantity
- recommendation priority

## 3.4 Deterministic recommendations remain authoritative

Actions:

```text
UNAVAILABLE
REORDER
REDUCE EXCESS
MONITOR / PREPARE
NO ACTION
```

Gemini can explain but cannot override the deterministic result.

## 3.5 Financial terminology

The current gross calculation is based on sales × selling price minus sales × unit cost.

Present it as:

```text
Estimated Profit
```

or:

```text
Estimated Gross Profit
```

Do not imply net profit after rent, salaries, utilities, tax, etc.

## 3.6 Business Health

Do not invent a 0–100 health score.

Use transparent indicators/counts such as:

```text
Products needing attention
Healthy products
Unavailable products
Inventory value
```

unless an explicit formula is later approved.

## 3.7 Deterministic priority ordering

Same-priority products must have deterministic ordering.

Document and use an explicit tie-breaker, e.g.:

```text
priority
→ stockout urgency where applicable
→ days remaining
→ product_id
```

Do not depend on arbitrary UI/dictionary ordering.

---

# 4. Date, Time, and Shipment Semantics

MVP business timezone:

```text
Asia/Phnom_Penh
```

Define and consistently use semantics for:

- sales dates
- inventory snapshots
- shipment expected arrival
- `as_of`
- refresh
- manual stock adjustment
- frontend date display

Explicitly define how a shipment with `expected_arrival = today` behaves.

Do not let different layers invent different date semantics.

---

# 5. Google Sheets Rules

Controlled MVP source:

```text
Google Sheets
├── Products
├── Sales
├── Inventory
└── Shipments
```

## 5.1 Write capability

Phase 2 verified reading, but stock adjustment requires writing.

Safely verify:

```text
authenticate
→ identify spreadsheet
→ identify Inventory sheet
→ update one test value
→ read it back
→ verify shipment data unchanged
→ restore original value
```

Never damage real demo data during the test.

## 5.2 Connection state

Do not call a sheet "Connected" merely because environment variables exist.

Use truthful states such as:

```text
Not Configured
Configured
Connected / Verified
Connection Error
```

## 5.3 Analysis snapshot / refresh

Avoid unnecessarily rereading the same sheet for one logical operation.

Prefer:

```text
Google Sheets
→ validated/processed snapshot
→ analytics
→ recommendations
→ verified AI context
```

Do not introduce complex caching unless justified.

"Refresh" means:

```text
Re-read source
→ validate/process
→ regenerate deterministic analysis
→ update UI
```

Gemini should not automatically run on every refresh unless explicitly required.

---

# 6. Gemini Rules

Gemini receives verified structured context, not raw spreadsheet rows.

It cannot:

- invent numbers
- invent shipments
- invent missing information
- change recommendation
- change reorder quantity
- change priority
- replace core calculations

Gemini failure must not break deterministic functionality.

Prefer lazy AI loading:

```text
Dashboard → AI brief after core data
Product Detail → AI explanation when requested
Analytics → AI insight when requested/appropriate
```

Before depending on a Gemini model, verify:

- model availability
- API access
- current account/plan
- structured-output support where required
- credentials
- quota/limits

Never assume an old model remains available.

---

# 7. Frontend Global Rules

## 7.1 Visual workflow

Figma MCP is NOT a project dependency.

Use:

```text
Source of Truth
+
Backend/API/OpenAPI
+
Written UI specification
+
Master visual reference
+
Optional page-specific references
→ OpenCode implementation
→ Visual QA
```

The master reference controls overall:

- layout
- visual identity
- colors
- style
- navigation
- component language
- page structure

Visual references do not override backend/API truth.

## 7.2 Backend data is authoritative

Never hardcode business data from mockups.

## 7.3 Null vs zero

```text
0 = known zero
null/unavailable = unknown or insufficient data
```

Never display unavailable values as zero.

## 7.4 UI states

Data-driven areas should handle:

- loading
- success
- empty
- unavailable
- API error
- Gemini unavailable
- refreshing/stale state

## 7.5 Product isolation

Switching products must never display stale stock, shipments, charts, recommendations, or AI explanations from another product.

## 7.6 Responsive design

Keep the application usable across likely demo desktop/tablet widths without unnecessary mobile architecture.

## 7.7 Components/dependencies

Use reusable components where useful.

Avoid over-componentization and unnecessary UI libraries/dependencies.

## 7.8 Status consistency

Use the same recommendation/status labels and visual language throughout the application.

## 7.9 AI presentation

AI supports understanding.

Do not create a giant chatbot.

Approved AI locations:

```text
Dashboard → AI Business Brief
Product Detail → See What AI Recommends
Analytics → AI Insight
```

---

# 8. Realistic Demo Dataset

Before serious frontend work, prepare realistic Cambodian mini-mart demo data containing:

- Khmer + English names
- realistic categories
- realistic prices
- realistic inventory
- varied demand patterns
- stockout cases
- excess cases
- incoming shipments
- healthy cases

The frontend must consume API data, not hardcode the dataset.

Keep realistic demo data separate from canonical test fixtures.

---

# PHASE 9 — PRE-FRONTEND FEASIBILITY & DEPENDENCY GATE

## Goal

Remove uncertainty before serious frontend development.

Phase 9 is a **triage + feasibility gate**, not a requirement to fix every concern immediately.

## Scope

Verify:

1. Google Sheets write capability
2. Google Sheets connection behavior
3. Gemini live capability/model/configuration
4. frontend ↔ backend communication
5. CORS
6. visual-reference workflow
7. deployment feasibility
8. current backend concerns
9. realistic demo dataset readiness
10. date/time semantics
11. stock-adjustment semantics
12. analysis snapshot/refresh semantics

## What NOT to Change

Do not build feature pages.

Do not replace working architecture.

Do not add authentication, multi-tenancy, databases, Figma MCP, AI agents, or new product features.

## Implementation Requirements

For each external dependency produce the dependency check.

Create/update `docs/CONCERNS.md`.

Classify concerns:

```text
CONFIRMED BUG
NEEDS DEFINITION
NEEDS IMPROVEMENT
ALREADY SAFE
NOT AN MVP PROBLEM
```

Resolve concerns that belong in Phase 9.

Assign later concerns to explicit owner phases.

Lock down MVP decisions for:

- timezone
- shipment-arrival-today behavior
- stock adjustment behavior
- refresh semantics
- snapshot behavior
- Business Profile persistence
- connection state
- deployment approach

## Tests

Run relevant existing backend tests.

Perform safe Sheets write/read/restore test.

Perform Gemini smoke test if credentials exist.

Test frontend/backend communication and CORS.

Test deployment feasibility.

## Verification

No critical external dependency remains an unverified assumption.

All unresolved material concerns have an owner, plan, and verification method.

## Reporting

Report every dependency check, concern classification, blocker, fix, deferral, demo-data status, and deployment finding.

## Exit Criteria

A verified path to frontend development exists.

---

# PHASE 10 — FRONTEND FOUNDATION

## Goal

Build the shared frontend shell and visual foundation.

## Scope

Implement:

- application shell
- navigation
- routes
- shared layout
- typography
- spacing
- status styles
- shared loading/error patterns
- API client
- shared API types
- visual language

## What NOT to Change

Do not implement feature-specific business logic.

Do not duplicate backend calculations.

Do not hardcode demo data.

## Implementation Requirements

Use real API contracts and approved visual references.

## Tests

- frontend build
- type checks
- route checks
- API client checks

## Verification

All primary routes have stable structural shells.

## Reporting

Report routes, shared components, dependencies, contract assumptions, tests.

## Exit Criteria

Frontend foundation is stable.

---

# PHASE 11 — DASHBOARD

## Goal

Create the action-oriented dashboard.

## Scope

```text
Business Health
Top Priorities
AI Business Brief
Historical Overview
```

The dashboard should answer:

```text
What is happening?
What needs attention?
What should I look at first?
```

## What NOT to Change

Do not invent health scores, business calculations, unsupported analytics, or a separate AI page.

## Implementation Requirements

Use API data.

Top Priorities must use deterministic backend ordering.

AI brief should load separately/lazily.

## Tests

Test:

- loading
- success
- empty
- API error
- Gemini unavailable
- priority ordering
- null/zero handling
- responsive layout

## Verification

Dashboard reflects backend truth and remains useful without Gemini.

## Reporting

Report API data consumed, state handling, and visual evidence.

## Exit Criteria

Dashboard is functional and visually aligned.

---

# PHASE 12 — INVENTORY + PRODUCT DETAIL

## Goal

Implement the core inventory workflow.

## Scope

Product list:

```text
Product
Category
Current Stock
Status
Days Remaining
Action
```

Product detail:

```text
Identity
Current Stock
Demand
Days Remaining
Inventory Value
Incoming Shipments
Recommendation
Evidence / Reasons
Historical Trend
See What AI Recommends
```

## What NOT to Change

Do not recalculate backend metrics, merge shipments into current stock, alter recommendation logic, or build autonomous ordering.

## Implementation Requirements

Product switching must clear/replace previous state safely.

Shipment data stays separate from current inventory.

AI explanation remains optional.

## Tests

Test multiple products, switching, missing products, unavailable metrics, shipment timing, recommendation rendering, Gemini failure, and UI states.

## Verification

Owner can understand what is happening, why, and what to do.

## Reporting

Provide evidence for product switching and recommendation rendering.

## Exit Criteria

Inventory/product-detail workflow works end to end.

---

# PHASE 13 — MANUAL STOCK ADJUSTMENT

## Goal

Allow safe physical stock updates.

## Scope

```text
Inventory
→ Adjust Stock
→ update current physical inventory
→ Google Sheets
→ Refresh
→ recalculate
```

## What NOT to Change

Do not modify shipments, create duplicate inventory rows, introduce a database, or move business calculations into frontend.

## Implementation Requirements

Use the semantics approved in Phase 9.

Prefer updating the latest inventory snapshot for the product rather than creating a duplicate product/date row, unless Phase 9 establishes another safe MVP method.

After adjustment, backend recalculates the result.

## Tests

Test valid adjustment, zero stock, restoration, invalid values, shipment unchanged, read-back, recommendation changes, duplicate prevention, and failure handling.

## Verification

Prove:

```text
UI
→ API
→ Google Sheets
→ read-back
→ refreshed analysis
```

## Reporting

Include before/after stock and recommendation evidence.

## Exit Criteria

Manual adjustment is safe and integrated.

---

# PHASE 14 — ANALYTICS UI

## Goal

Provide useful, honest analytics.

## Scope

```text
Demand
Inventory
Financial
Historical Trends
AI Insight
```

## What NOT to Change

Do not add advanced forecasting or unsupported statistical claims.

## Implementation Requirements

Charts use API data.

Historical charts clearly represent supported data.

Use Estimated Profit / Estimated Gross Profit wording.

AI Insight explains trends rather than becoming the source of truth.

## Tests

Test chart mappings, missing/zero values, empty data, historical data, API failures, AI unavailable, responsive charts.

## Verification

Analytics do not misrepresent data or certainty.

## Reporting

List each chart and API source.

## Exit Criteria

Analytics are accurate, useful, and visually consistent.

---

# PHASE 15 — SETTINGS + SHEETS CONNECTION

## Goal

Implement lightweight configuration.

## Scope

```text
Business Profile
Google Sheets Connection
Refresh / connection state
```

## What NOT to Change

Do not build authentication, multi-tenancy, or credential-management UI.

## Implementation Requirements

Use the Business Profile persistence approach approved in Phase 9.

Connection state must be truthful.

Never expose secrets.

## Tests

Test profile behavior, connection states, missing configuration, failures, refresh, and secret exposure.

## Verification

Settings accurately represents the one connected mini-mart.

## Reporting

Explain persistence and connection-state behavior.

## Exit Criteria

Settings works without SaaS architecture creep.

---

# PHASE 16 — FULL END-TO-END INTEGRATION

## Goal

Prove InventoryIQ works as one system.

## Scope

Test:

```text
Google Sheets
→ validation
→ processing
→ analysis snapshot
→ analytics
→ recommendations
→ verified AI context
→ Gemini
→ FastAPI
→ frontend
```

Owner journey:

```text
Open InventoryIQ
↓
Connect / refresh data
↓
See what needs attention
↓
Open product
↓
Understand why
↓
See recommended action
↓
Adjust stock if needed
↓
Refresh
↓
See updated recommendation
```

## What NOT to Change

Do not add features during E2E.

## Implementation Requirements

Reuse canonical scenarios:

```text
Healthy
Immediate stockout
Shipment before stockout
Shipment after stockout
Excess / slow-moving
Increasing demand
```

Also use realistic Cambodian demo data.

Verify snapshot/refresh semantics.

Verify Gemini cannot alter deterministic results.

## Tests

Test full pipeline, stock adjustment, shipment timing, zero demand, missing inventory, Gemini failure, API failures, refresh, product switching, realistic demo data, and canonical scenarios.

## Verification

Trace at least one scenario through the actual production pipeline from source data to UI.

## Reporting

Report every stage and every remaining concern.

## Exit Criteria

The system works as one integrated product.

---

# PHASE 17 — COMPREHENSIVE TESTING + BUSINESS AUDIT

## Goal

Test InventoryIQ as a business product, not merely as software.

## Scope

Test all important scenarios and edge cases, including:

- healthy
- stockout
- excess
- shipments before/after stockout
- increasing/decreasing/stable demand
- zero demand
- missing data
- invalid data
- duplicates
- insufficient history
- empty data
- single/multiple products
- multiple categories
- Khmer/English/mixed names

## What NOT to Change

Do not add features because of interesting test discoveries.

## Implementation Requirements

Compare behavior against the Source of Truth.

Audit business correctness, recommendation correctness, data semantics, API contracts, frontend behavior, AI guardrails, and error handling.

## Tests

Run the complete backend suite and frontend checks.

## Verification

Every failure becomes:

```text
fixed
deferred
accepted
out of scope
```

with appropriate documentation.

## Reporting

Provide a business-rule audit, not only a test count.

## Exit Criteria

No unexplained business-critical failures remain.

---

# PHASE 18 — VISUAL QA + UX AUDIT

## Goal

Ensure the product looks and feels like the intended InventoryIQ design.

## Scope

Review:

- Dashboard
- Inventory
- Product Detail
- Analytics
- Settings
- navigation
- loading/error/empty states
- AI states
- responsive layouts
- typography
- spacing
- colors
- visual hierarchy
- recommendation/status presentation

## What NOT to Change

Do not change business behavior or add features during visual QA.

## Implementation Requirements

Compare against the master visual reference, page references, and written UI specification.

Prioritize:

```text
layout
design
colors
style
hierarchy
consistency
```

over insignificant pixel-level differences.

## Tests

Manual visual review across representative screen sizes.

## Verification

No major visual/UX defect harms the live demo.

## Reporting

Report:

```text
Issue
Severity
Fix
Verification
```

## Exit Criteria

Frontend is demo-ready visually.

---

# PHASE 19 — SECURITY + RELIABILITY + SCOPE AUDIT

## Goal

Perform the final engineering and scope audit.

## Scope

Check:

- secrets
- environment variables
- service-account credentials
- Gemini key exposure
- frontend exposure
- error messages
- stack traces
- CORS
- unsafe writes
- input validation
- deployment configuration
- dependency risks
- stale state
- Google Sheets failures
- Gemini failures
- scope creep
- unnecessary infrastructure

## What NOT to Change

Do not add enterprise architecture or features.

## Implementation Requirements

Distinguish acceptable MVP limitations from actual security/reliability problems.

## Tests

Run security checks, safe failure injection, dependency checks, and production configuration checks.

## Verification

No critical secret exposure, destructive write path, or demo-breaking reliability problem remains.

## Reporting

Report:

```text
Security findings
Reliability findings
Scope findings
Accepted limitations
Remaining concerns
```

## Exit Criteria

InventoryIQ is appropriately secure and reliable for the MVP/demo context.

---

# PHASE 20 — DEPLOYMENT + DEMO READINESS

## Goal

Prove InventoryIQ works outside localhost.

## Scope

Verify:

```text
Frontend hosting
Backend hosting
Environment variables
Google service account
Google Sheets access
Gemini API
CORS
HTTPS
Frontend API URL
Startup behavior
Demo dataset
```

## What NOT to Change

Do not introduce unnecessary production infrastructure.

## Implementation Requirements

Use environment configuration for secrets.

Test:

```text
deployed frontend
→ deployed backend
→ Google Sheets
→ deterministic analysis
→ Gemini
```

Check cold starts and free-tier/hosting reliability.

Prepare a demo fallback if a non-critical AI service fails.

## Tests

Run the owner journey against the deployed environment.

Test refresh, stock adjustment, Gemini failure, and backend failure states.

## Verification

The actual deployed application works.

## Reporting

Provide deployment status, configuration checklist, known limitations, fallback plan, and final concerns.

## Exit Criteria

InventoryIQ can be demonstrated from the deployed environment.

---

# PHASE 21 — FINAL RELEASE CHECK

## Goal

Final no-new-features release gate.

## Scope

Review:

- Source of Truth
- Architecture
- `docs/CONCERNS.md`
- API/OpenAPI
- frontend
- backend
- tests
- deployment
- demo flow
- visual quality
- security/reliability
- MVP scope

## What NOT to Change

Do not add features or perform speculative refactors.

## Implementation Requirements

Confirm:

```text
All MVP features have coverage.
All major concerns have a final status.
No critical blockers remain.
Frontend uses backend truth.
Gemini remains non-authoritative.
Google Sheets write path works.
Deployment works.
Demo dataset works.
Owner journey works.
No secrets are committed.
```

## Tests

Run:

- final backend suite
- frontend build/checks
- deployed smoke test
- final owner journey

## Verification

Review every remaining `docs/CONCERNS.md` item.

Nothing critical may remain unexplained.

Known limitations must be explicitly marked.

## Reporting

Use:

```text
RELEASE CHECK

MVP features:
Backend:
Frontend:
Google Sheets:
Gemini:
E2E:
Visual QA:
Security:
Deployment:
Open concerns:
Known limitations:
Demo readiness:
```

## Exit Criteria

InventoryIQ is ready for the intended hackathon demonstration.

The agent stops.

**whitelist reviews and performs the final commit/push manually.**

---

# Final Principle

The remaining phases should make InventoryIQ:

```text
Correct
↓
Useful
↓
Reliable
↓
Clear
↓
Visually polished
↓
Demo-ready
```

Do not optimize for complexity.

Optimize for a reliable product that a Cambodian mini-mart owner can actually understand and use.

The frontend presents backend truth in the InventoryIQ visual design.

The deterministic backend turns mini-mart data into actionable inventory decisions.

Gemini makes those decisions easier to understand.

Google Sheets remains the practical MVP data source.

Every material concern must be tracked until it is resolved, deferred, accepted, or explicitly removed from scope.
