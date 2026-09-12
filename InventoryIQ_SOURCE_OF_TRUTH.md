# InventoryIQ --- Source of Truth

**Project:** InventoryIQ\
**MVP Audience:** Cambodian mini-mart owners only

> This document is the complete source of truth for what InventoryIQ is,
> what the MVP must build, and what is intentionally outside the MVP.

------------------------------------------------------------------------

# Part 1 --- Our Goal

## 1.1 Who Are We Building For?

InventoryIQ is built specifically for **small mini-mart owners in
Cambodia**.

Typical target business:

-   Family-run or small local mini-mart
-   Around 50--200 SKUs
-   Uses a spreadsheet, notebook, or simple records
-   Does not have a dedicated data analyst
-   Needs simple and practical inventory decisions

We are **not** building a general inventory product for every type of
business.

------------------------------------------------------------------------

## 1.2 What Problem Are We Trying to Solve?

Mini-mart owners can lose money in two major ways:

### Stockouts

Fast-moving products can sell out before the owner realizes they need to
restock.

Example:

> Coca-Cola 330ml is selling quickly and may run out in 4 days, but the
> next shipment arrives in 6 days.

The owner may only notice the problem after the product is already
unavailable.

### Excess / Slow-Moving Stock

Products that sell slowly can remain on shelves for long periods.

This ties up:

-   Cash
-   Shelf space
-   Inventory investment

The owner may not realize which products are creating this problem.

### The underlying problem

Mini-marts may already have sales and inventory data, but the owner has
to manually interpret it.

> **The problem is not simply a lack of data. The problem is turning
> existing data into useful inventory decisions.**

------------------------------------------------------------------------

## 1.3 How Are We Going To Solve It?

InventoryIQ acts as an **intelligence layer on top of the mini-mart's
existing data**.

``` text
Mini-Mart Data
      ↓
InventoryIQ
      ↓
Understand sales + inventory
      ↓
Detect problems
      ↓
Recommend an action
      ↓
Explain the recommendation with Gemini
      ↓
Owner takes action
```

The product should answer four simple questions:

``` text
1. What is happening?
2. What needs attention?
3. What should I do?
4. Why?
```

------------------------------------------------------------------------

## 1.4 Core Product Principle

> **InventoryIQ turns mini-mart data into decisions the owner can
> actually act on.**

We prioritize actionable information over complicated analytics.

The owner should not need to be a data analyst to understand the
product.

------------------------------------------------------------------------

# Part 2 --- InventoryIQ MVP

## 2.1 MVP Rule

**Everything listed in Part 2 is the MVP.**

This is the complete list of functionality that needs to be built for
the MVP.

If a feature is not listed here, it is **not an MVP requirement**.

Do not add extra functionality without explicitly deciding to expand the
scope.

------------------------------------------------------------------------

# 3. Data Source --- Google Sheets

InventoryIQ's MVP uses **Google Sheets as the primary data source**.

The spreadsheet contains four tabs:

``` text
Google Sheets
│
├── Products
├── Sales
├── Inventory
└── Shipments
```

Google Sheets is the source of business data. InventoryIQ provides the
intelligence on top of it.

------------------------------------------------------------------------

## 3.1 Products

``` text
product_id
product_name
category
unit
unit_cost
selling_price
supplier
lead_time_days
target_stock_days
```

Used to store information about each mini-mart product.

------------------------------------------------------------------------

## 3.2 Sales

``` text
date
product_id
quantity_sold
```

Used to understand how quickly each product is selling.

------------------------------------------------------------------------

## 3.3 Inventory

``` text
date
product_id
quantity_on_hand
```

Daily inventory history is required.

`quantity_on_hand` represents the observed physical inventory for that
date.

------------------------------------------------------------------------

## 3.4 Shipments

``` text
shipment_id
product_id
quantity
expected_arrival
```

Represents future incoming supplier stock.

The MVP does not require:

``` text
actual_arrival
status
```

------------------------------------------------------------------------

# 4. Data Processing

InventoryIQ processes the Google Sheets data before analysis.

``` text
Google Sheets
      ↓
Read
      ↓
Validate
      ↓
Clean / Normalize
      ↓
Combine
      ↓
Analysis-ready data
```

The MVP should reliably support the defined Google Sheets structure.

Basic validation must detect problems such as:

-   Missing sheets
-   Missing columns
-   Invalid dates
-   Invalid numbers
-   Unknown product IDs
-   Duplicate records where inappropriate
-   Invalid shipment dates

### Important data rule

**Missing data is not automatically zero.**

For example:

``` text
Missing inventory ≠ 0 inventory
```

If there is not enough reliable data to calculate something, the system
should show it as unavailable rather than inventing a value.

------------------------------------------------------------------------

# 5. Inventory Tracker

The Inventory Tracker gives the owner a clear view of their products.

For each product, InventoryIQ can show:

-   Product name
-   Category
-   Current stock
-   Stock status
-   Days of stock remaining
-   Inventory value
-   Demand
-   Incoming shipments
-   Recommendation

------------------------------------------------------------------------

## 5.1 Product List

The owner can:

-   View products
-   Search products
-   Filter products
-   See stock status
-   See days remaining
-   Open a product's details

Example:

``` text
Coca-Cola 330ml     24 units    🔴 Low       3.0 days
Indomie Chicken     45 packs    🟢 Healthy   18 days
ABC Soy Milk        10 bottles  🟠 Excess    40 days
```

------------------------------------------------------------------------

## 5.2 Product Detail

Clicking a product opens its detailed inventory view.

It should show:

``` text
Product
│
├── Current Stock
├── Demand
├── Days Remaining
├── Inventory Value
├── Incoming Shipments
├── Recommendation
├── Evidence / Reasons
├── Historical Trend
└── AI Explanation (GEMINI)
```

------------------------------------------------------------------------

# 6. Sales & Demand Analytics

InventoryIQ analyzes product sales.

For each product, where sufficient data exists, calculate:

-   Total units sold
-   Average daily sales
-   Recent demand
-   Demand trend
-   Increasing / Stable / Decreasing

The purpose is not to show statistics for their own sake.

The purpose is to understand:

> **How quickly is this product moving, and is demand changing?**

------------------------------------------------------------------------

# 7. Inventory Analytics

InventoryIQ analyzes current and historical inventory.

Calculate:

-   Current stock
-   Inventory value
-   Days of stock remaining
-   Stockout risk
-   Excess inventory

------------------------------------------------------------------------

# 8. Incoming Shipment Analysis

InventoryIQ considers future incoming stock when analyzing inventory.

For relevant shipments, calculate/use:

-   Incoming quantity
-   Expected arrival date
-   Days until arrival
-   Expected future inventory
-   Whether current stock may run out before arrival

Example:

``` text
Current stock: 24
Average sales: 8/day
Shipment: 50 units
Arrival: 5 days

Current stock lasts ≈ 3 days
Shipment arrives in 5 days

→ Potential stockout before shipment
```

The recommendation engine must consider this timing.

------------------------------------------------------------------------

# 9. Financial Analytics

Where the required data exists, InventoryIQ calculates:

-   Revenue
-   Estimated cost
-   Profit
-   Profit margin
-   Inventory value
-   Financial exposure

If required information is missing, do not invent the result.

------------------------------------------------------------------------

# 10. Stockout Detection

InventoryIQ identifies products that may run out before they can be
safely restocked.

It considers:

``` text
Current stock
+
Demand
+
Lead time
+
Incoming shipment timing
```

The output should be understandable to the owner.

Example:

> Coca-Cola 330ml may run out in approximately 4 days, while the
> incoming shipment arrives in 6 days.

------------------------------------------------------------------------

# 11. Excess Inventory Detection

InventoryIQ identifies products with materially more stock than their
expected/target coverage.

Show useful information such as:

-   Excess units
-   Excess inventory value
-   Relevant evidence

Example:

> Instant noodles have had very low sales recently and approximately
> \$180 of stock is tied up.

------------------------------------------------------------------------

# 12. Recommendation Engine

This is the deterministic decision-making part of InventoryIQ.

The system produces:

``` text
🔴 REORDER
🟠 REDUCE EXCESS
🟡 MONITOR / PREPARE
🟢 NO ACTION
⚪ UNAVAILABLE
```

------------------------------------------------------------------------

## 12.1 REORDER

Used when inventory is at meaningful stockout risk.

The system should determine:

-   Whether to reorder
-   Recommended reorder quantity
-   Recommended timing
-   Whether incoming stock is sufficient
-   Evidence behind the decision

------------------------------------------------------------------------

## 12.2 REDUCE EXCESS

Used when a product has materially excessive/slow-moving stock.

The system should show:

-   Why it is considered excess
-   Excess quantity/value where available

The owner may then decide whether to discount, return, or otherwise
reduce the stock.

------------------------------------------------------------------------

## 12.3 MONITOR / PREPARE

Used when there is a meaningful trend or developing risk that does not
require an immediate reorder.

Example:

> Demand has been increasing recently. Consider preparing additional
> stock for future demand.

The MVP should use simple trend logic, not advanced forecasting.

------------------------------------------------------------------------

## 12.4 NO ACTION

Used when the product is currently healthy and does not require
intervention.

------------------------------------------------------------------------

## 12.5 UNAVAILABLE

Used when insufficient or invalid data prevents a reliable
recommendation.

The system must not pretend to know the answer.

------------------------------------------------------------------------

# 13. Recommendation Logic

Recommendation priority should be:

``` text
1. UNAVAILABLE
2. Stockout / REORDER
3. EXCESS
4. FUTURE PREPARATION
5. MONITOR
6. NO ACTION
```

Immediate stockout risk takes priority over a secondary
future-preparation signal.

------------------------------------------------------------------------

## 13.1 Reorder Quantity

Conceptually:

``` text
Recommended reorder quantity
=
Desired stock
-
Expected available stock
```

The exact implementation formula must be explicitly defined and tested
during development.

The calculation belongs to the backend, not the frontend.

------------------------------------------------------------------------

# 14. Gemini AI

Gemini is an **AI explanation and contextualization layer**.

It is not the source of truth.

``` text
Google Sheets
      ↓
Processing
      ↓
Analytics
      ↓
Recommendation Engine
      ↓
Verified Structured Context
      ↓
Gemini
      ↓
Plain-language explanation
```

------------------------------------------------------------------------

## 14.1 What Gemini Does

Gemini can:

-   Explain recommendations
-   Summarize business conditions
-   Explain trends
-   Highlight important priorities
-   Give simple contextual advice based only on verified data

------------------------------------------------------------------------

## 14.2 What Gemini Does NOT Do

Gemini must not:

-   Calculate core metrics
-   Invent numbers
-   Invent missing data
-   Invent shipments
-   Override deterministic recommendations
-   Assume missing information

The backend remains authoritative.

------------------------------------------------------------------------

# 15. Where Gemini Appears

Gemini is intentionally placed where it is useful.

``` text
🏠 Dashboard
│
└── 🤖 AI Business Brief (GEMINI)
    → High-level summary of the business

📦 Inventory
│
└── Product Detail
    │
    └── ✨ See What AI Recommends (GEMINI)
        → Expandable explanation of the recommendation

📊 Analytics
│
└── ✨ AI Insight (GEMINI)
    → Explains meaningful trends
```

There is **no separate AI page**.

------------------------------------------------------------------------

# 16. AI Business Brief --- Dashboard

The Dashboard should contain a Gemini-powered business summary.

Example:

> "Three products need attention. Coca-Cola 330ml is the highest
> priority because current stock may run out before the next shipment
> arrives."

Purpose:

> **Give the owner a quick understanding of what is happening.**

------------------------------------------------------------------------

# 17. AI Recommendation --- Product Detail

The product detail recommendation can expand.

Example:

``` text
🔴 REORDER

Recommended: 24 units

Your stock may run out before the next shipment.

[ ✨ See What AI Recommends ˅ ]
```

When expanded:

``` text
✨ AI Recommendation

Your current stock is expected to last about
4 days, while the incoming shipment arrives
in 5 days.

Demand has also been increasing, so ordering
24 additional units can reduce the risk of
a stockout.
```

The deterministic recommendation appears first. Gemini explains it.

------------------------------------------------------------------------

# 18. AI Insight --- Analytics

Analytics can contain a small Gemini insight card.

Example:

``` text
✨ AI Insight

Beverage sales have increased over the past
two weeks. Consider preparing additional stock
for products with the strongest demand.
```

This is based on verified backend analysis.

------------------------------------------------------------------------

# 19. Business Health --- Dashboard

The Dashboard should immediately summarize the business.

Useful overview information:

-   Items needing attention
-   Healthy items
-   Total inventory value
-   Overall inventory/business health

The goal is:

> **Tell the owner what matters before they start exploring details.**

------------------------------------------------------------------------

# 20. Top Priorities --- Dashboard

The Dashboard should surface products requiring action.

Example:

``` text
🔴 Coca-Cola 330ml
Low stock
Reorder 24 units
Runs out in ~4 days

🟠 Instant Noodles
Excess stock
$180 tied up

🟡 Pepsi 330ml
Demand increasing
Prepare for higher demand
```

Clicking a priority should take the owner to the relevant product
detail.

------------------------------------------------------------------------

# 21. Historical Overview

The Dashboard can contain a lightweight historical chart.

The purpose is to provide quick context, not advanced statistical
analysis.

The full historical analysis belongs on the Analytics page.

------------------------------------------------------------------------

# 22. Analytics Page

The Analytics page allows the owner to investigate the business.

``` text
Analytics
│
├── Demand
├── Inventory
├── Financial
├── Historical Trends
└── AI Insight (GEMINI)
```

It should remain simple and readable.

------------------------------------------------------------------------

# 23. Manual Stock Adjustment

The owner can manually correct the current physical inventory.

``` text
Inventory
      ↓
Adjust Stock
      ↓
Update current inventory
      ↓
Google Sheets
      ↓
Refresh
      ↓
Recalculate
```

This is separate from shipments.

Example:

``` text
Current stock = 15
Incoming shipment = 50
```

These remain two separate values.

------------------------------------------------------------------------

# 24. Settings

Settings should remain lightweight.

``` text
Settings
│
├── Business Profile
└── Google Sheets Connection
```

### Business Profile

-   Business name
-   Business type
-   Basic required business information

### Google Sheets Connection

-   Connect/load sheet
-   Connection state
-   Refresh/reconnect
-   Last update/sync information where available

------------------------------------------------------------------------

# 25. Complete Website Structure

``` text
InventoryIQ
│
├── 🏠 Dashboard
│   │
│   ├── Business Health
│   ├── Top Priorities
│   ├── AI Business Brief (GEMINI)
│   └── Historical Overview
│
├── 📦 Inventory
│   │
│   ├── Product List
│   ├── Search / Filter
│   │
│   ├── Product Detail
│   │   ├── Current Stock
│   │   ├── Demand
│   │   ├── Incoming Shipments
│   │   ├── Recommendation
│   │   ├── Evidence / Reasons
│   │   ├── Historical Trend
│   │   └── See What AI Recommends (GEMINI)
│   │
│   └── Manual Stock Adjustment
│
├── 📊 Analytics
│   │
│   ├── Demand
│   ├── Inventory
│   ├── Financial
│   ├── Historical Trends
│   └── AI Insight (GEMINI)
│
└── ⚙️ Settings
    ├── Business Profile
    └── Google Sheets Connection
```

------------------------------------------------------------------------

# 26. Ideal User Flow

``` text
Open InventoryIQ
      ↓
Dashboard
      ↓
See what needs attention
      ↓
Click a product
      ↓
See recommendation + evidence
      ↓
Click "See What AI Recommends"
      ↓
Read Gemini explanation
      ↓
Take action
      ↓
Adjust stock if necessary
      ↓
Refresh
      ↓
See updated analysis
```

------------------------------------------------------------------------

# 27. Technical Architecture

``` text
                    InventoryIQ
                         │
                         ▼
                 React / Next.js
                 + Tailwind CSS
                         │
                       API
                         │
                         ▼
                       FastAPI
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   Google Sheets     Analysis       Gemini API
          │           Engine            │
          │              │              │
          └──────────────┴──────────────┘
                         │
                         ▼
                    Recommendations
```

## Stack

### Frontend

-   React / Next.js
-   Tailwind CSS

### Backend

-   Python
-   FastAPI
-   Pandas

### Data

-   Google Sheets

### AI

-   Gemini API

### Design

-   Figma

### Development

-   OpenCode

------------------------------------------------------------------------

# 28. Core Backend Flow

``` text
Google Sheets
      ↓
Validation
      ↓
Data Processing
      ↓
Analytics Engine
      ↓
Recommendation Engine
      ↓
Verified AI Context
      ↓
Gemini
      ↓
API Response
      ↓
Frontend
```

The backend owns the business logic.

The frontend displays the results.

------------------------------------------------------------------------

# 29. Testing Requirements

The MVP must test the real end-to-end flow:

``` text
Google Sheets
→ Processing
→ Analytics
→ Recommendation
→ AI Context
→ API
→ Frontend
```

Important scenarios:

-   Healthy product
-   Stockout risk
-   Excess inventory
-   Shipment arriving before stockout
-   Shipment arriving after projected stockout
-   Increasing demand
-   Decreasing demand
-   Stable demand
-   Zero demand
-   Missing inventory
-   Missing sales
-   Missing shipment
-   Missing lead time
-   Missing cost/price
-   Invalid dates
-   Invalid numbers
-   Negative inventory
-   Duplicate product/date records
-   Insufficient history
-   Empty data
-   Single product
-   Multiple products/categories
-   Khmer product names
-   English product names
-   Mixed Khmer/English names

The system must also verify:

-   Missing inventory is not treated as zero.
-   Current stock and incoming stock remain separate.
-   Reorder quantity is calculated by the backend.
-   Frontend does not recreate core recommendation calculations.
-   Gemini cannot override deterministic recommendations.
-   Missing information results in an unavailable state where required.
-   Gemini failure does not break the core product.
-   Invalid calculations do not crash the application.

Visual QA is also required for layout, loading/error states, stale
product state, long names, and Khmer/English text.

------------------------------------------------------------------------

# 30. UI / Figma Rules

Figma is the design blueprint. The coded frontend is the actual
application.

The UI should be:

-   Clean
-   Simple
-   Mini-mart-specific
-   Easy for a non-technical owner to understand
-   Action-oriented
-   Not overloaded with charts

The design team can change:

-   Colors
-   Typography
-   Layout
-   Card styles
-   Navigation
-   Chart design
-   AI presentation
-   Visual hierarchy

But the feature relationships and required information in this document
should remain.

Before building the real UI, perform a small Figma → MCP → OpenCode →
localhost test.

------------------------------------------------------------------------

# Part 3 --- Proposed Future Features

> **Everything in this section is intentionally NOT part of the MVP.**

These are proposed directions for the future product and business model.

------------------------------------------------------------------------

# 31. Dynamic / Messy Spreadsheet Input

Future InventoryIQ should eventually handle less structured real-world
data.

Potential capabilities:

-   Messy spreadsheets
-   Different spreadsheet layouts
-   Inconsistent formatting
-   Mixed Khmer/English
-   More flexible column structures
-   Automatic data normalization

Future concept:

``` text
Messy Spreadsheet
      ↓
InventoryIQ understands structure
      ↓
Normalize
      ↓
Analyze
```

The MVP uses a controlled Google Sheets structure first.

------------------------------------------------------------------------

# 32. Supplier Connection

Future InventoryIQ could connect mini-mart owners directly with
suppliers.

Concept:

``` text
InventoryIQ
      ↓
🔴 Reorder 50 units
      ↓
Connected Supplier
      ↓
Order directly
      ↓
Supplier fulfills
      ↓
Inventory updates
```

This could support a **supplier transaction commission model**.

The actual supplier marketplace/order integration is not an MVP feature.

------------------------------------------------------------------------

# 33. Freemium + Paid Subscription

Future business model:

``` text
InventoryIQ
│
├── Free
│   └── Core inventory intelligence
│
└── Paid
    └── Advanced features / automation
```

The exact paid features and pricing can be decided after validating the
MVP.

No payment or subscription billing is required in the MVP.

------------------------------------------------------------------------

# 34. Future Integrations

Potential future integrations:

-   POS systems
-   Accounting systems
-   Bank/payment data
-   Supplier systems
-   Automated inventory updates
-   Other business data sources

These are roadmap ideas only.

------------------------------------------------------------------------

# 35. Future Product Direction

The long-term vision is:

``` text
Existing Business Data
        ↓
InventoryIQ
        ↓
Understand everything
        ↓
Detect problems
        ↓
Recommend actions
        ↓
Connect owner to supplier
        ↓
Automate more of the inventory workflow
```

The MVP should first prove the core value:

> **Can InventoryIQ reliably turn mini-mart sales and inventory data
> into decisions that owners understand and act on?**

------------------------------------------------------------------------

# 36. Final Scope Rule

For MVP development:

**Build everything in Part 2.**

**Do not build anything from Part 3.**

Do not add unrelated features during implementation.

If a new idea appears, first determine whether it is:

-   Required for the MVP → add explicitly to the MVP scope.
-   Useful but not required → put it in the future roadmap.
-   Unnecessary → do not build it.

------------------------------------------------------------------------

# 37. Final Product Definition

> **InventoryIQ is an inventory decision assistant specifically for
> Cambodian mini-mart owners. It reads their sales, inventory, and
> incoming-shipment data, identifies stockout and excess-stock problems,
> recommends practical actions, and uses Gemini to explain those
> recommendations in simple language.**

The core promise is:

``` text
Their data
   ↓
InventoryIQ
   ↓
Clear insight
   ↓
Clear action
   ↓
Better inventory decisions
```

**This document is the complete source of truth for the InventoryIQ
MVP.**
