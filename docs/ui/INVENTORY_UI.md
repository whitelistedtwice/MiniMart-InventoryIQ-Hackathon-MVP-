INVENTORYIQ — INVENTORY UI SPECIFICATION

==================================================
1. INVENTORY SECTION PURPOSE
==================================================

The Inventory section is where the mini-mart owner views their products, understands current stock conditions, opens individual product analysis, and sees InventoryIQ's recommendations.

The Inventory section contains:

1. Inventory List
2. Product Detail
3. AI Product Insight

The Inventory section should remain simple and action-oriented.

The owner should be able to:

Search products
→ Filter inventory
→ Identify products needing attention
→ Open Product Detail
→ Understand the recommendation
→ Read the AI explanation


==================================================
2. IMPORTANT MVP SCOPE
==================================================

InventoryIQ currently uses Google Sheets as its source of inventory/product data.

Products originate from the connected Google Sheet.

The current MVP is primarily a READ/ANALYSIS system.

IMPORTANT:

Manual Stock Adjustment is NOT currently implemented.

There is NO supported InventoryIQ → Google Sheets stock write-back workflow in the current MVP.

Therefore:

- Do NOT implement an "Adjust Stock" button.
- Do NOT implement a stock adjustment modal.
- Do NOT implement a stock editing form.
- Do NOT implement inventory write-back functionality.
- Do NOT invent an inventory update API endpoint.
- Do NOT implement product creation.
- Do NOT implement product editing.
- Do NOT implement product deletion.

The Inventory section should only display and analyze the inventory data supplied by the backend.

This is intentional MVP scope.

If manual stock adjustment/write-back is added in the future, it must first be implemented, tested, and added to the Source of Truth/backend contracts before being added to the frontend.


==================================================
3. AUTHORITY ORDER
==================================================

When implementing the Inventory section, use this authority order:

1. InventoryIQ Source of Truth
2. Backend API contracts
3. This UI specification
4. Visual reference images

The backend and Source of Truth define:

- data meaning
- calculations
- recommendation logic
- missing-data behavior
- available functionality

The visual references define:

- layout
- spacing
- typography
- colors
- card styling
- table styling
- visual hierarchy

Visual references do NOT define new functionality.

If a visual reference conflicts with the backend/API/Source of Truth, the backend/API/Source of Truth wins.


==================================================
4. OVERALL VISUAL STYLE
==================================================

Use the approved InventoryIQ visual language.

The Inventory section should be:

- clean
- simple
- modern
- professional
- lightweight
- spacious
- easy to scan

Use:

- very light background
- white cards
- subtle borders
- subtle shadows
- modest rounded corners
- dark navy text
- blue primary actions
- green healthy states
- red urgent states
- orange/yellow warning states
- light purple/lavender AI sections
- simple outline icons
- clean sans-serif typography

Do not introduce unnecessary visual complexity.

Do not add decorative components that do not improve usability.


==================================================
5. GLOBAL INVENTORY LAYOUT
==================================================

The Inventory section uses the application's shared:

- left sidebar
- top navigation
- typography
- spacing system
- account controls

Inventory should be highlighted as the active navigation item.

The three Inventory views are:

Inventory List
→ Product Detail
→ AI Product Insight


==================================================
6. VISUAL REFERENCE: inventory/main.png
==================================================

Reference:

docs/visual-references/inventory/main.png

This image represents the primary Inventory List view.

Use it for:

- page composition
- sidebar
- top bar
- page header
- search controls
- filter controls
- table layout
- status badges
- pagination
- spacing
- typography
- overall visual density

The example products and values are illustrative.

Do not hard-code them.


==================================================
7. INVENTORY LIST PAGE
==================================================

Page title:

Inventory

Supporting text:

Manage your products and stock levels.

The page should immediately show the product inventory table.

There should NOT be an Add Product button.

There should NOT be an Adjust Stock button.

The page is primarily a product overview and analysis view.


==================================================
8. SEARCH
==================================================

Provide a search field near the top of the Inventory page.

Suggested placeholder:

Search products...

Search should allow the user to quickly locate products.

Use product information supplied by the backend.

Do not invent a separate search backend if client-side filtering of the already-loaded inventory response is sufficient.

Search should be fast and simple.


==================================================
9. CATEGORY FILTER
==================================================

Provide a category filter.

Default:

All Categories

The available category values should come from the actual product data.

Do not hard-code categories that do not exist.

Filtering must not change or recalculate the underlying inventory metrics.


==================================================
10. STATUS FILTER
==================================================

Provide a status filter.

Default:

All Statuses

Status values must correspond to the backend's established recommendation/status system.

Do not invent new statuses.

Do not calculate status in the frontend.


==================================================
11. INVENTORY TABLE
==================================================

The main Inventory component is a product table.

Recommended columns:

- Product
- Category
- Current Stock
- Status
- Days Left
- Last Updated
- Actions

The exact displayed fields must be based on the existing API response.

Do not create fields that the backend does not provide.

The table should be spacious and easy to scan.


==================================================
12. PRODUCT COLUMN
==================================================

Display:

- product name
- product image/icon only when supported

Product names come from backend data.

The UI must support:

- English names
- Khmer names
- mixed Khmer/English names

Do not assume every product has an image.

If an image is unavailable, use a simple consistent fallback.


==================================================
13. CATEGORY COLUMN
==================================================

Display the product category supplied by the backend.

Category text should be visually secondary to the product name.

Do not invent categories.


==================================================
14. CURRENT STOCK COLUMN
==================================================

Display the current physical stock supplied by the backend.

The unit should come from the product data.

Examples such as:

18 L
500 pcs
12 kg

are illustrative only.

Important:

Current stock and incoming shipments are separate.

Do NOT combine them.

For example:

Current stock = 15
Incoming shipment = 50

must NOT become:

Current stock = 65

Incoming stock affects recommendation and future inventory analysis, but it is not current physical stock.


==================================================
15. STATUS COLUMN
==================================================

Display the backend-provided recommendation/status.

Use the established InventoryIQ visual meanings:

REORDER
→ red / urgent

REDUCE EXCESS
→ orange/red / warning

MONITOR / PREPARE
→ yellow/orange / attention

NO ACTION
→ green / healthy

UNAVAILABLE
→ neutral/gray / insufficient data

Do not recalculate these states in the frontend.

Do not create alternative labels that change their meaning.


==================================================
16. DAYS LEFT COLUMN
==================================================

Display backend-provided days of stock remaining.

Do NOT calculate days remaining in the frontend.

If the backend provides a valid number, display it clearly.

If the backend provides insufficient data:

Do NOT display 0.

Show an appropriate unavailable/insufficient-data state.

Missing data is not zero.


==================================================
17. LAST UPDATED
==================================================

If a valid timestamp is provided by the backend/application state, display it in a human-readable format.

Examples:

2 minutes ago
1 hour ago
1 day ago

These are examples only.

Do not fabricate timestamps.

If a valid timestamp is unavailable, display an appropriate fallback or omit the field.


==================================================
18. INVENTORY ACTIONS
==================================================

Actions should remain minimal.

The primary action is:

Open Product Detail

Clicking a product should navigate to the Product Detail view.

Do NOT add:

- Add Product
- Edit Product
- Delete Product
- Duplicate Product
- Adjust Stock
- Edit Supplier
- Edit Product Metadata

These are outside current MVP scope.


==================================================
19. PRODUCT DETAIL
==================================================

Visual reference:

docs/visual-references/inventory/product-detail.png

Product Detail provides a deeper view of one product.

It should show information such as:

- product identity
- category
- unit
- current stock
- days of stock remaining
- average daily demand
- incoming shipments
- historical stock trend
- deterministic recommendation
- evidence/reasons
- AI Product Insight

The Product Detail page should remain focused on helping the owner understand the product.

Do NOT add unrelated product-management functionality.


==================================================
20. PRODUCT DETAIL HEADER
==================================================

The header should clearly identify the selected product.

Example:

Milk

Category:
Dairy

Unit:
L

The example is illustrative.

Use actual backend data.

Provide a clear navigation option:

Back to Inventory


IMPORTANT:

There must NOT be an Adjust Stock button.

The current MVP does not support manual stock modification.


==================================================
21. PRODUCT DETAIL SUMMARY
==================================================

Use compact summary cards for important product information.

Supported information may include:

Current Stock

Days Left

Average Daily Demand

Incoming Shipments

Only display metrics actually provided by the backend.

Do not independently calculate these metrics in the frontend.


==================================================
22. CURRENT STOCK AND SHIPMENTS
==================================================

Current stock represents observed physical inventory.

Incoming shipments represent stock that has not yet arrived.

These must remain visually and logically separate.

Example:

Current Stock:
18 L

Incoming Shipment:
30 L

Arrives in 5 days

Do not display 48 L as current stock.


==================================================
23. STOCK TREND
==================================================

If historical inventory data is available from the backend, show a simple stock-level trend chart.

The chart should be:

- clean
- easy to read
- lightweight
- visually consistent with Analytics

Use backend-provided historical data.

Do not fabricate historical values.

Do not implement advanced forecasting here.


==================================================
24. RECOMMENDATION
==================================================

Product Detail should prominently display the deterministic recommendation.

Possible actions:

REORDER
REDUCE EXCESS
MONITOR / PREPARE
NO ACTION
UNAVAILABLE

If the recommendation is REORDER, show the backend-provided recommended reorder quantity when available.

Example:

Reorder 12 L

The example is illustrative.

The frontend must NOT calculate the reorder quantity.


==================================================
25. RECOMMENDATION EVIDENCE
==================================================

Show concise reasons/evidence supporting the recommendation.

Examples:

Stock may run out before the next shipment arrives.

Current stock is higher than expected demand.

Demand has been increasing recently.

These should be based on backend-provided evidence.

Do not generate business logic in the frontend.


==================================================
26. AI PRODUCT INSIGHT
==================================================

Visual reference:

docs/visual-references/inventory/ai-product-insight.png

AI Product Insight is an expandable AI explanation associated with the deterministic recommendation.

The user can open it to understand:

- why the recommendation makes sense
- what the demand pattern looks like
- how incoming shipments affect the situation
- what action is recommended
- useful contextual notes

The AI section should use a light lavender/purple visual treatment.

It should feel helpful and distinct without becoming a chatbot.


==================================================
27. AI PRODUCT INSIGHT COLLAPSED STATE
==================================================

When collapsed, show a compact entry such as:

AI Product Insight

or:

See What AI Recommends

Use a sparkle/AI icon.

The collapsed state should not take up excessive space.


==================================================
28. AI PRODUCT INSIGHT EXPANDED STATE
==================================================

When expanded, show a concise structured explanation.

Suggested structure:

AI Product Insight

Why this recommendation?

[AI explanation]

Recommended action

[Backend recommendation]

Why?

[Verified supporting evidence]

Demand trend

[Verified demand context]

Upcoming shipment

[Verified shipment context]

Additional note

[AI-generated contextual explanation based on verified data]


The exact content must depend on available verified context.

Do not force every subsection to appear if the backend does not provide the required information.


==================================================
29. AI RULES
==================================================

The AI architecture is:

Google Sheets
→ validation/processing
→ analytics
→ deterministic recommendation
→ verified structured context
→ Gemini
→ explanation

Gemini is an explanation layer.

Gemini must NOT:

- calculate core metrics
- calculate reorder quantities
- invent shipments
- invent sales
- invent inventory
- override recommendations
- assume missing data
- fabricate financial values

The deterministic backend remains the authority.


==================================================
30. AI FAILURE
==================================================

If Gemini is unavailable:

The Product Detail page must still work.

The following must remain available:

- product information
- inventory information
- demand information
- shipment information
- deterministic recommendation
- evidence/reasons

The AI section should gracefully indicate that AI insight is unavailable.

Do not show fake AI-generated content.

Do not expose API keys, stack traces, or raw backend errors.


==================================================
31. PRODUCT DETAIL API
==================================================

Use the existing backend endpoint:

GET /api/v1/inventory/{product_id}

Do not create another product-detail endpoint unless the backend architecture explicitly changes.

The frontend should not access Google Sheets directly.


==================================================
32. INVENTORY LIST API
==================================================

Use the existing backend endpoint:

GET /api/v1/inventory

The frontend should consume the backend response.

Do not duplicate backend calculations in React/Next.js.


==================================================
33. AI PRODUCT INSIGHT API
==================================================

Use the existing backend AI recommendation endpoint where applicable:

GET /api/v1/ai/recommendation/{product_id}

Use the existing response contract.

Do not invent a separate AI endpoint.

If AI is unavailable, use the backend's existing availability/error state.


==================================================
34. LOADING STATES
==================================================

Inventory List:

Show table skeletons while loading.

Product Detail:

Show lightweight skeletons for:

- product header
- metric cards
- recommendation
- trend chart
- AI section

Do not display fake values while loading.


==================================================
35. EMPTY STATES
==================================================

If no inventory exists:

Show a clear empty state.

If search/filter produces no results:

Show:

No products found

Do not confuse filtered-empty results with a broken data source.

If Product Detail cannot find a valid product:

Show an appropriate product-not-found state.


==================================================
36. ERROR STATES
==================================================

API errors should produce clear user-friendly messages.

Provide retry/refresh where appropriate.

Do NOT expose:

- stack traces
- raw exceptions
- API keys
- credentials
- internal infrastructure details


==================================================
37. MISSING DATA
==================================================

InventoryIQ has strict missing-data semantics.

IMPORTANT:

Missing inventory ≠ zero inventory.

Missing demand ≠ zero demand.

Missing shipment data ≠ no shipment.

Missing financial input ≠ zero financial value.

The frontend must preserve backend null/unavailable states.

Never silently replace missing values with zero.


==================================================
38. RESPONSIVE DESIGN
==================================================

Desktop is the primary MVP target.

On smaller screens:

- sidebar may collapse
- cards may stack
- filters may wrap
- tables may scroll horizontally
- product information should remain accessible
- AI insight should remain readable

Do not create a completely separate mobile application.


==================================================
39. VISUAL CONSISTENCY
==================================================

Inventory List, Product Detail, and AI Product Insight must feel like parts of the same application.

Use consistent:

- colors
- typography
- spacing
- cards
- buttons
- status badges
- icons
- navigation

The Product Detail page should visually connect to the Inventory List.

The AI Product Insight should use the same light lavender AI treatment used elsewhere in InventoryIQ.


==================================================
40. VISUAL REFERENCE RULE
==================================================

The visual reference images are not feature specifications.

They communicate appearance only.

If an image contains a feature that is not supported by the current backend/API/Source of Truth:

DO NOT IMPLEMENT IT.

In particular:

The current Inventory MVP does NOT support:

- Manual Stock Adjustment
- Inventory write-back
- Product creation
- Product editing
- Product deletion

Therefore, do not implement UI for these features even if an old/reference image contains them.

The current approved Product Detail reference should be interpreted without an Adjust Stock control.


==================================================
41. ACCEPTANCE CRITERIA
==================================================

Inventory List:

- [ ] Clean and simple layout.
- [ ] Inventory is active in sidebar.
- [ ] Search works.
- [ ] Category filter works.
- [ ] Status filter works.
- [ ] Product table is readable.
- [ ] Current stock comes from backend.
- [ ] Units come from product data.
- [ ] Incoming shipments are not merged with current stock.
- [ ] Status comes from backend.
- [ ] Days Left comes from backend.
- [ ] Missing values are not converted to zero.
- [ ] Product opens Product Detail.
- [ ] Pagination works when required.
- [ ] Loading state exists.
- [ ] Empty state exists.
- [ ] Error state exists.
- [ ] No Add Product button.
- [ ] No Edit Product functionality.
- [ ] No Delete Product functionality.
- [ ] No Adjust Stock functionality.

Product Detail:

- [ ] Product identity is clear.
- [ ] Back to Inventory works.
- [ ] Current stock is displayed.
- [ ] Days remaining is displayed when available.
- [ ] Demand is displayed when available.
- [ ] Incoming shipments are displayed separately.
- [ ] Historical stock trend is displayed when supported.
- [ ] Deterministic recommendation is clearly visible.
- [ ] Recommendation quantity comes from backend.
- [ ] Recommendation evidence is shown.
- [ ] AI Product Insight can be expanded/collapsed.
- [ ] AI content uses verified backend context.
- [ ] Gemini cannot override deterministic recommendation.
- [ ] AI failure does not break Product Detail.
- [ ] No Adjust Stock button.
- [ ] No product editing controls.
- [ ] No unsupported functionality.

Overall:

- [ ] Inventory pages visually match Dashboard, Analytics, and Settings.
- [ ] Light blue/green/red visual language is consistent.
- [ ] AI sections use a subtle lavender treatment.
- [ ] No unnecessary features are introduced.
- [ ] No unsupported API endpoints are introduced.
- [ ] No frontend business logic duplicates backend calculations.
- [ ] Realistic Cambodian mini-mart data renders correctly.
- [ ] Khmer, English, and mixed-language product names render correctly.


==================================================
42. FINAL PRINCIPLE
==================================================

InventoryIQ is not trying to be a full inventory management system yet.

The Inventory section is an intelligence and decision-support interface.

The core flow is:

Google Sheets
→ InventoryIQ
→ Analyze
→ Detect issues
→ Recommend
→ Explain with Gemini
→ Owner understands what to do

Keep the UI clean.

Keep the functionality focused.

Do not add features simply because they are common in inventory software.

Only implement functionality supported by the current Source of Truth and backend contracts.