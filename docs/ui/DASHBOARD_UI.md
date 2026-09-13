InventoryIQ — Dashboard UI Specification

IMPORTANT IMPLEMENTATION RULES

This document defines the complete frontend UI specification for the Dashboard page.

The Dashboard has two visual references:

1. docs/visual-references/dashboard/main.png
2. docs/visual-references/dashboard/ai-business-brief.png

Authority order:

1. InventoryIQ Source of Truth
2. Backend API contracts
3. This UI specification
4. Visual reference images

The Source of Truth and backend contracts define what data, calculations, recommendations, and functionality actually exist.

The visual references are DESIGN REFERENCES ONLY.

Use the images to understand:

- layout
- spacing
- typography
- colors
- card styling
- navigation
- visual hierarchy
- component appearance
- overall visual language

Do NOT treat example numbers, products, dates, text, charts, or AI responses in the images as real production data.

Do NOT invent features, endpoints, metrics, calculations, or business logic based only on the images.

The frontend must present backend-provided information rather than recreating business logic.


==================================================
1. DASHBOARD PURPOSE
==================================================

The Dashboard is the owner's high-level overview of their mini-mart.

It should answer:

- How is my inventory doing?
- What needs my attention?
- What should I act on first?
- What is happening with my business?
- What does the AI think is important?

The Dashboard should be action-oriented.

Do NOT turn it into a wall of charts.

The owner should be able to understand the most important situation within a few seconds.


==================================================
2. OVERALL VISUAL STYLE
==================================================

Use the approved InventoryIQ visual style shown in the Dashboard and Product Detail references.

The design should be:

- clean
- modern
- simple
- professional
- lightweight
- spacious
- easy to scan

Use:

- very light overall background
- white cards
- subtle borders
- subtle shadows
- modest rounded corners
- dark navy primary text
- blue primary actions
- green positive/healthy states
- red urgent states
- yellow/orange warning states
- light purple/lavender for AI sections
- simple outline icons
- clean sans-serif typography

The Dashboard should use the same visual language as Inventory, Product Detail, Analytics, and Settings.

Do not introduce a different design system for the Dashboard.


==================================================
3. GLOBAL PAGE LAYOUT
==================================================

The Dashboard consists of:

1. Left sidebar
2. Top navigation bar
3. Dashboard header
4. Business Health / summary area
5. Top Priorities
6. AI Business Brief
7. Historical overview where supported

Keep the main content visually balanced.

Avoid excessive cards and unnecessary sections.


==================================================
4. SIDEBAR
==================================================

Use the same sidebar throughout the application.

Navigation:

- Dashboard
- Inventory
- Analytics
- Settings

Dashboard is the active navigation item.

The active item should use the established blue highlight treatment.

Do not create Dashboard-specific sidebar behavior.


==================================================
5. TOP BAR
==================================================

Use the same global top bar as the other pages.

It may contain:

- search
- notification icon
- business/account identity
- existing global controls

Do not invent functionality for decorative controls.

The top bar should remain visually consistent across all pages.


==================================================
6. DASHBOARD HEADER
==================================================

The main page should have a clear Dashboard heading.

Suggested supporting text:

"Here's what needs your attention today."

Keep the heading compact.

Do not use excessive explanatory text.


==================================================
7. BUSINESS HEALTH / SUMMARY
==================================================

The Dashboard should provide a quick overview of the current business/inventory situation.

Use backend-supported summary information.

The summary should help answer:

- how many products need attention
- how many products are healthy
- total inventory value when available

Example visual concepts may include:

- Need Attention
- Healthy
- Total Inventory Value

Example values in the reference image are illustrative only.

Do not hard-code them.

Do not invent a numerical "Business Health Score".

InventoryIQ does NOT currently have a defined Business Health scoring algorithm.

Therefore:

DO NOT create a percentage score, grade, or health number unless explicitly added to the Source of Truth and backend contract later.


==================================================
8. TOP PRIORITIES
==================================================

The Dashboard should prominently display the most important inventory actions.

Use the deterministic recommendation engine provided by the backend.

The frontend must NOT decide priority itself.

The established recommendation priority order is:

1. UNAVAILABLE
2. Stockout / REORDER
3. EXCESS
4. FUTURE PREPARATION
5. MONITOR
6. NO ACTION

Display the most important products first according to the backend's recommendation/priority information.

Example visual structure:

Top Priorities

1. Reorder Milk
   Likely to run out soon

2. Reorder Sugar
   Stock is low based on current demand

3. Reduce excess Chocolate Syrup
   Stock is higher than expected demand

These examples are illustrative only.

Use real backend data.

Each priority item should make the recommended action immediately understandable.

Where supported, clicking a priority should navigate to the relevant Product Detail page.


==================================================
9. RECOMMENDATION STATUS COLORS
==================================================

Use the established InventoryIQ status language.

REORDER:
- red
- urgent

REDUCE EXCESS:
- orange/red
- warning

MONITOR / PREPARE:
- yellow/orange
- attention

NO ACTION:
- green
- healthy

UNAVAILABLE:
- neutral/gray
- insufficient data

Do not create new recommendation categories in the frontend.

Do not change the meaning of backend statuses.


==================================================
10. AI BUSINESS BRIEF
==================================================

The AI Business Brief is the main AI-powered section on the Dashboard.

Reference:

docs/visual-references/dashboard/ai-business-brief.png

The AI Business Brief provides a short natural-language explanation of the current business situation.

It should help the owner understand:

- what is happening
- what needs attention
- why it matters
- what actions are worth considering

It should be concise.

It is NOT a chatbot.


==================================================
11. AI BUSINESS BRIEF LOCATION
==================================================

The AI Business Brief should appear as a prominent Dashboard section.

Use a light lavender/purple-tinted card to visually distinguish AI-generated content from deterministic business metrics.

The AI section should still feel integrated into the Dashboard.

Do not make it visually overwhelming.


==================================================
12. AI BUSINESS BRIEF HEADER
==================================================

Use an AI/sparkle icon and a clear heading:

"AI Business Brief"

Optional supporting text:

"Your daily overview powered by AI. Here's what you need to know today."

Keep the supporting text short.


==================================================
13. AI BUSINESS BRIEF CONTENT
==================================================

The AI Business Brief should summarize verified business context.

Possible content:

- overall inventory condition
- important products requiring attention
- major demand trends
- significant inventory risks
- useful near-term context

The content must be generated from the verified structured context provided by the backend.

Gemini should explain the existing data.

Gemini must NOT become the source of truth for business calculations.


==================================================
14. AI BUSINESS BRIEF DATA RULES
==================================================

The AI Business Brief must use:

Google Sheets
→ validation/processing
→ analytics
→ deterministic recommendation
→ verified structured AI context
→ Gemini
→ AI Business Brief

Gemini may:

- explain recommendations
- summarize business conditions
- describe trends
- highlight important priorities
- provide simple contextual advice based on verified data

Gemini must NOT:

- calculate core inventory metrics
- calculate reorder quantities
- invent sales
- invent inventory
- invent shipments
- invent financial values
- override deterministic recommendations
- assume missing information
- convert missing data into zero
- create unsupported business claims


==================================================
15. AI FAILURE BEHAVIOR
==================================================

AI must never be required for the core Dashboard to function.

If Gemini is unavailable:

- Dashboard metrics should still work
- inventory priorities should still work
- deterministic recommendations should still work
- the AI section should gracefully show that the insight is unavailable

Do not show fake AI content as if it came from Gemini.

Do not expose:

- API keys
- stack traces
- raw exceptions
- internal errors

The backend already provides an AI availability state.

Use that state.


==================================================
16. AI BUSINESS BRIEF ACTION
==================================================

If the existing backend/API supports an appropriate detailed AI insight navigation path, the UI may provide a link/action to the relevant Analytics or insight view.

Do not invent an AI endpoint or separate AI page.

There is currently no standalone AI page in the InventoryIQ MVP.

Do not create:

- AI Chat
- AI Assistant
- Ask AI Anything
- AI conversation history
- AI prompt box


==================================================
17. HISTORICAL OVERVIEW
==================================================

The Dashboard may contain a lightweight historical overview where supported by existing backend data.

The purpose is to show how the business/inventory has changed over time.

Keep this simple.

Possible supported information includes:

- historical inventory value
- sales/demand trend
- previous-period comparison

Only display information that is actually provided by the backend.

Do not create new analytics calculations inside the frontend.

Do not add advanced forecasting or statistical analysis to the Dashboard.


==================================================
18. INVENTORY VALUE
==================================================

Inventory value may be displayed when valid backend financial data is available.

The frontend should display the backend-provided inventory value.

Do not calculate it independently.

Do not fabricate values when unit cost or inventory data is missing.

Financial values must respect the backend's missing-data semantics.


==================================================
19. SEARCH / NAVIGATION
==================================================

If global search exists, keep its behavior consistent across pages.

The Dashboard should not implement a separate search system.

Product navigation should lead to the existing Inventory/Product Detail routes.


==================================================
20. LOADING STATE
==================================================

While Dashboard data is loading:

- show lightweight skeletons/placeholders
- preserve the page structure
- avoid a blank screen

Do not show fake business data while loading.


==================================================
21. EMPTY STATE
==================================================

If there is insufficient or empty source data:

Show a clear, helpful empty/insufficient-data state.

Do not fabricate:

- products
- sales
- inventory
- financial values
- recommendations
- AI summaries

Remember:

Missing data does NOT mean zero.


==================================================
22. ERROR STATE
==================================================

If a Dashboard API request fails:

- show a clear user-friendly error
- provide retry/refresh where appropriate
- preserve the overall page structure

Do NOT expose:

- stack traces
- raw backend exceptions
- credentials
- API keys
- infrastructure information

Use the existing structured backend error response.


==================================================
23. FRONTEND VS BACKEND RESPONSIBILITIES
==================================================

FRONTEND SHOULD:

- display Dashboard data
- display summary metrics
- display backend recommendation priorities
- format values
- navigate to relevant pages
- display AI Business Brief
- manage loading states
- manage empty states
- manage errors
- refresh data when appropriate

FRONTEND MUST NOT:

- calculate recommendation priority
- calculate reorder quantities
- calculate stockout risk
- calculate days remaining
- calculate excess inventory
- invent a Business Health score
- calculate financial metrics independently
- override backend recommendations
- invent missing data
- turn missing values into zero
- invent API endpoints
- invent AI capabilities


==================================================
24. CURRENT DASHBOARD API
==================================================

The Dashboard should use the existing backend API contract.

Primary Dashboard endpoint:

GET /api/v1/dashboard

AI Business Brief:

GET /api/v1/ai/business-brief

Use the existing API response structures.

Do not create duplicate endpoints for the same information.

Do not make the frontend directly access Google Sheets.

The frontend communicates with the FastAPI backend.


==================================================
25. DATA REFRESH
==================================================

Dashboard data should represent the latest successful backend response.

Do not create an independent browser-side source of truth.

When refreshed:

- request current backend data
- replace stale Dashboard data
- update visible sections consistently

Avoid situations where the priority list shows old data while metrics show new data.


==================================================
26. RESPONSIVE DESIGN
==================================================

Desktop is the primary MVP target.

On smaller screens:

- sidebar may collapse according to the global application layout
- cards may stack vertically
- AI Business Brief should remain readable
- priority items should remain easy to scan
- charts may resize
- avoid excessive horizontal scrolling

Do not create a completely separate mobile application design.


==================================================
27. VISUAL REFERENCE: dashboard/main.png
==================================================

Reference:

docs/visual-references/dashboard/main.png

Use this image for:

- Dashboard layout
- sidebar
- top navigation
- page header
- summary card styling
- priority section styling
- AI section placement
- spacing
- typography
- general visual hierarchy

The image is NOT a functional specification.

Example data shown in the image is illustrative only.

Do not implement unsupported sections simply because they appear in the image.

If the image conflicts with the Source of Truth or backend API:

Source of Truth/backend wins.


==================================================
28. VISUAL REFERENCE: dashboard/ai-business-brief.png
==================================================

Reference:

docs/visual-references/dashboard/ai-business-brief.png

Use this image to understand the expanded/featured presentation of the AI Business Brief.

Focus on:

- light lavender AI card
- AI sparkle icon
- clear heading
- concise summary
- important takeaways
- red/orange/green status cues
- simple visual hierarchy
- clean spacing

The image does NOT mean InventoryIQ should implement every element shown.

Only use data and functionality supported by the backend/API contract.

Do not implement:

- AI chat
- AI prompt input
- AI conversation history
- unsupported forecast features
- unsupported customer analytics
- unsupported metrics


==================================================
29. AI BUSINESS BRIEF UX PRINCIPLE
==================================================

The AI Business Brief should feel like a helpful business summary, not a chatbot.

The user should be able to glance at it and understand:

"What is going on?"

"What should I care about?"

"Why?"

The deterministic recommendation engine remains the authority.

Gemini provides the explanation layer.


==================================================
30. ACCEPTANCE CRITERIA
==================================================

The Dashboard is complete only when:

- [ ] Dashboard follows the approved InventoryIQ visual style.
- [ ] Sidebar matches the rest of the application.
- [ ] Dashboard is clearly the active navigation item.
- [ ] Dashboard header is present.
- [ ] Summary information comes from backend data.
- [ ] No invented Business Health score exists.
- [ ] Top Priorities use backend recommendation data.
- [ ] Recommendation priority follows backend ordering.
- [ ] Status colors match established recommendation meanings.
- [ ] Product priorities can navigate to Product Detail where supported.
- [ ] AI Business Brief is visually distinct but integrated.
- [ ] AI Business Brief uses the existing backend AI endpoint.
- [ ] AI content is based on verified structured context.
- [ ] Gemini cannot override deterministic recommendations.
- [ ] AI failure does not break the Dashboard.
- [ ] Missing data is not silently converted to zero.
- [ ] Financial values are not fabricated.
- [ ] Historical information is only displayed when supported.
- [ ] No unsupported endpoints are created.
- [ ] No AI chatbot functionality is created.
- [ ] Loading state exists.
- [ ] Empty/insufficient-data state exists.
- [ ] Error state exists.
- [ ] No secrets or raw backend errors are exposed.
- [ ] Dashboard does not become overloaded with unnecessary charts/cards.
- [ ] Dashboard works with the realistic Cambodian mini-mart dataset.
- [ ] Dashboard remains visually consistent with Inventory, Analytics, and Settings.


==================================================
31. FINAL DESIGN PRINCIPLE
==================================================

The Dashboard should be the fastest way for a mini-mart owner to understand what matters today.

Keep the experience simple:

See the situation
→ See what needs attention
→ Understand why
→ Take action

The backend owns the business logic.

The recommendation engine owns the decision.

Gemini explains the verified information.

The frontend makes everything easy to understand.