INVENTORYIQ — ANALYTICS UI SPECIFICATION



==================================================

1\. ANALYTICS SECTION PURPOSE

==================================================



The Analytics section helps the mini-mart owner understand their business data over time.



It should answer:



\- How much are we selling?

\- What products/categories are driving demand?

\- What is happening with inventory?

\- What is the financial position?

\- What trends are changing?

\- What should I pay attention to?



The Analytics page is for understanding patterns and trends.



It is NOT intended to replace the Inventory page's action-oriented recommendations.



The core flow is:



View business data

→ understand trends

→ identify meaningful changes

→ use AI Insight for a plain-language explanation





==================================================

2\. ANALYTICS SUBSECTIONS

==================================================



The Analytics section contains:



1\. Analytics Overview

2\. Demand Analytics

3\. Inventory Analytics

4\. Financial Analytics

5\. Historical Trends

6\. AI Insight



These should be presented within the Analytics experience.



Do NOT create separate pages for every subsection unless the existing application architecture explicitly requires it.





==================================================

3\. IMPORTANT MVP SCOPE

==================================================



AnalyticsIQ's Analytics system is intentionally simple.



The MVP focuses on:



\- demand

\- inventory

\- financial information

\- historical trends

\- simple recent-vs-historical comparisons

\- AI explanation of meaningful trends



The MVP does NOT include:



\- advanced forecasting

\- machine-learning forecasting

\- customer analytics

\- customer segmentation

\- customer lifetime value

\- stock turnover metrics unless explicitly supported by the backend

\- predictive revenue models

\- advanced statistical dashboards

\- arbitrary business intelligence metrics

\- AI-generated calculations



Do not implement these features simply because they are common in analytics products.





==================================================

4\. AUTHORITY ORDER

==================================================



When implementing Analytics, use this authority order:



1\. InventoryIQ Source of Truth

2\. Backend API contracts

3\. This UI specification

4\. Visual reference images



The backend owns:



\- calculations

\- metric definitions

\- trend calculations

\- financial calculations

\- missing-data semantics

\- AI context



The visual references only communicate:



\- layout

\- spacing

\- typography

\- colors

\- chart appearance

\- visual hierarchy



If the visual reference contains a feature that is not supported by the backend/API:



DO NOT IMPLEMENT IT.





==================================================

5\. OVERALL VISUAL STYLE

==================================================



Use the established InventoryIQ visual language.



Analytics should be:



\- clean

\- light

\- modern

\- professional

\- easy to scan

\- information-rich without feeling crowded



Use:



\- very light background

\- white cards

\- subtle borders

\- subtle shadows

\- modest rounded corners

\- dark navy text

\- blue primary accents

\- green positive states

\- red warning/negative states

\- orange/yellow attention states

\- light purple/lavender AI sections

\- simple charts

\- clean sans-serif typography



Analytics should visually match:



\- Dashboard

\- Inventory

\- Product Detail

\- Settings



Do not introduce a completely different visual style.





==================================================

6\. VISUAL REFERENCE: analytics/main.png

==================================================



Reference:



docs/visual-references/analytics/main.png



Use this image for:



\- Analytics page composition

\- sidebar

\- top navigation

\- page header

\- summary cards

\- chart layout

\- tables

\- spacing

\- typography

\- general visual hierarchy



The example data in the image is illustrative only.



Do not hard-code:



\- sales values

\- quantities

\- categories

\- percentages

\- dates

\- product names

\- trend values



Use actual backend data.





==================================================

7\. ANALYTICS PAGE HEADER

==================================================



Page title:



Analytics



Supporting text:



Understand your sales, inventory and trends. Make better decisions with your data.



Keep the header simple.



A date-range control may be placed on the right side.



The selected date range should control the supported analytics data shown on the page.



Do not create unsupported date-range behavior.





==================================================

8\. DATE RANGE

==================================================



Analytics should provide a clear date-range control where supported.



Examples:



\- Last 7 days

\- Last 30 days

\- Last 90 days

\- Custom range



Only provide options that the backend can support correctly.



The selected range should be passed through the existing API contract where applicable.



Do not calculate a different date range in the frontend.



If a date range contains insufficient data, show the appropriate unavailable/insufficient-data state.





==================================================

9\. ANALYTICS OVERVIEW

==================================================



The top of Analytics should provide a small number of high-value summary metrics.



Possible supported metrics include:



\- Revenue

\- Total Units Sold

\- Inventory Value

\- Profit

\- Margin

\- Products Requiring Attention



Only show metrics provided by the backend.



Do not create excessive KPI cards.



The goal is quick understanding, not maximum information density.





==================================================

10\. DEMAND ANALYTICS

==================================================



Demand analytics explains how products are selling.



Supported concepts include:



\- total units sold

\- average daily sales

\- recent demand

\- demand trend

\- increasing demand

\- stable demand

\- decreasing demand

\- product/category demand comparisons



The backend owns all demand calculations.



The frontend only presents the results.





==================================================

11\. SALES / DEMAND TREND

==================================================



Use a simple line or equivalent chart for historical demand/sales when supported.



The chart should make it easy to see:



\- whether demand is increasing

\- whether demand is stable

\- whether demand is decreasing

\- major changes over time



Keep the chart visually simple.



Avoid excessive:



\- gridlines

\- labels

\- colors

\- annotations

\- decorative elements



Use blue as the primary analytical visualization color, with established status colors only when meaningful.





==================================================

12\. DEMAND TREND INTERPRETATION

==================================================



If the backend provides a demand trend classification:



\- Increasing → positive/attention context

\- Stable → neutral/healthy context

\- Decreasing → appropriate neutral/attention context



Do not determine these classifications from frontend chart data.



Use the backend's trend result.





==================================================

13\. PRODUCT DEMAND

==================================================



Analytics may show product-level demand comparisons where supported.



Useful examples include:



\- highest-selling products

\- lowest-selling products

\- quantity sold

\- revenue generated



These should come from backend analytics.



Do not introduce a customer-facing ranking system that changes the meaning of the data.





==================================================

14\. CATEGORY ANALYTICS

==================================================



Analytics may show category-level performance when category data is available.



Possible information:



\- units sold by category

\- revenue by category

\- category demand share



Use simple visualizations such as:



\- bar charts

\- simple comparison charts

\- carefully used donut/pie charts where appropriate



Do not overload the page with multiple versions of the same information.





==================================================

15\. INVENTORY ANALYTICS

==================================================



Inventory analytics helps the owner understand the overall state of their inventory.



Supported concepts include:



\- current inventory

\- inventory value

\- products requiring attention

\- stock levels

\- days of stock remaining where relevant

\- excess inventory

\- stockout risk

\- incoming inventory



The backend owns these calculations.



Do not create a frontend inventory scoring system.





==================================================

16\. INVENTORY VALUE

==================================================



Inventory value may be displayed when valid unit cost and inventory information are available.



The backend calculates the value.



The frontend displays it.



Do not independently calculate inventory value.



If required financial inputs are missing:



Do not display a fabricated value.



Show the appropriate unavailable state.





==================================================

17\. STOCKOUT / EXCESS OVERVIEW

==================================================



Analytics may summarize how many products fall into important inventory conditions.



Possible categories:



\- REORDER

\- REDUCE EXCESS

\- MONITOR / PREPARE

\- NO ACTION

\- UNAVAILABLE



Use the backend recommendation/status information.



Do not create a separate frontend classification system.





==================================================

18\. INCOMING SHIPMENTS

==================================================



Incoming shipments may be represented when supported by the analytics response.



Remember:



Current stock and incoming stock are separate.



For example:



Current inventory:

15 units



Incoming:

50 units



Do not display:



65 units current stock



Shipment timing matters to inventory analysis.



Do not ignore expected arrival dates.





==================================================

19\. FINANCIAL ANALYTICS

==================================================



Financial analytics may include:



\- revenue

\- estimated cost

\- profit

\- margin

\- inventory value

\- financial exposure



Only display metrics for which the backend has valid required inputs.



The backend owns financial calculations.



The frontend must never fabricate financial values.





==================================================

20\. REVENUE

==================================================



Revenue should come from backend analytics.



Use the existing financial calculation defined by the backend.



Display:



\- current-period revenue

\- historical comparison where available

\- trend direction where supported



Do not independently multiply sales quantities and selling prices in the frontend.





==================================================

21\. ESTIMATED COST

==================================================



Estimated cost may be displayed when unit cost information is available.



If unit cost is missing:



Do not assume cost is zero.



Show the appropriate unavailable/insufficient-data state.





==================================================

22\. PROFIT

==================================================



Profit may be displayed when revenue and cost data are sufficiently available.



If required inputs are missing:



Do not display a fabricated profit.



Do not interpret missing profit as zero.





==================================================

23\. MARGIN

==================================================



Margin should only be shown when the backend provides a valid calculation.



Avoid divide-by-zero or invalid denominator issues.



The frontend must not perform the calculation itself.





==================================================

24\. FINANCIAL EXPOSURE

==================================================



Financial exposure may be shown when supported by the backend.



This can help communicate the financial impact of inventory conditions.



For example, excess inventory can represent cash tied up in stock.



Only use backend-supported values.



Do not invent a financial-risk score.





==================================================

25\. HISTORICAL TRENDS

==================================================



Historical Trends are a core part of Analytics.



The purpose is to help the owner understand how the business has changed.



Supported historical information may include:



\- sales over time

\- units sold over time

\- inventory value over time

\- inventory levels over time

\- recent demand compared with historical demand



Keep historical analysis straightforward.



Do not introduce advanced statistical models.





==================================================

26\. RECENT VS HISTORICAL DEMAND

==================================================



InventoryIQ prepares for the future using simple comparisons rather than advanced forecasting.



Where supported, compare:



Recent demand



against



Historical demand



This can identify simple patterns such as:



\- increasing

\- stable

\- decreasing



The comparison must come from the backend.



Do not implement machine-learning forecasting in the frontend.





==================================================

27\. FUTURE PREPARATION

==================================================



Analytics can surface future-preparation context when supported by the recommendation/analytics backend.



For example:



Demand is increasing.



This may help the owner prepare inventory.



However, Analytics should not create its own reorder recommendation.



The deterministic recommendation engine remains responsible for inventory actions.





==================================================

28\. AI INSIGHT

==================================================



Visual reference:



docs/visual-references/analytics/ai-insight.png



AI Insight explains meaningful patterns found in the Analytics data.



It should help answer:



\- What changed?

\- Why is it important?

\- What should the owner pay attention to?



The AI Insight is an explanation layer.



It is NOT a separate analytics engine.





==================================================

29\. AI INSIGHT PRESENTATION

==================================================



Use a light lavender/purple AI section.



Suggested structure:



AI Insight



Overall Insight



\[Short AI-generated summary]



Key Takeaways



\- \[Meaningful verified trend]

\- \[Meaningful verified inventory condition]

\- \[Meaningful financial/demand observation]



Detailed Insights



\[Relevant explanation of supported analytics]





Keep the text concise.



Avoid large paragraphs.





==================================================

30\. AI INSIGHT DATA SOURCE

==================================================



The AI flow is:



Google Sheets

→ validation/processing

→ analytics

→ verified structured AI context

→ Gemini

→ AI Insight



Gemini should explain verified analytics results.



Gemini must NOT calculate the underlying analytics itself.





==================================================

31\. AI INSIGHT RULES

==================================================



Gemini may:



\- summarize trends

\- explain meaningful changes

\- highlight important patterns

\- explain inventory conditions

\- provide simple contextual advice based on verified data



Gemini must NOT:



\- invent numbers

\- invent sales

\- invent inventory

\- invent financial values

\- invent shipments

\- calculate core metrics independently

\- override deterministic recommendations

\- assume missing information

\- create unsupported forecasts





==================================================

32\. AI FAILURE BEHAVIOR

==================================================



Analytics must work without Gemini.



If Gemini is unavailable:



\- analytics charts still work

\- metrics still work

\- historical trends still work

\- financial information still works when supported

\- inventory analytics still work



The AI Insight section should gracefully indicate that AI insight is unavailable.



Do not show fake AI content.



Do not expose:



\- API keys

\- stack traces

\- raw backend exceptions

\- internal infrastructure information





==================================================

33\. NO CUSTOMER ANALYTICS

==================================================



Do NOT implement customer analytics.



The visual reference may contain generic analytics-style tabs or concepts such as:



\- Customers

\- Customer behavior

\- Customer segments



These are NOT part of InventoryIQ's current MVP.



Do not add them.





==================================================

34\. NO ADVANCED FORECASTING

==================================================



Do NOT implement advanced forecasting.



InventoryIQ currently uses simple recent-vs-historical demand comparisons.



Do not add:



\- machine-learning forecasts

\- predictive demand models

\- confidence intervals

\- complex forecasting charts

\- predicted revenue models



unless explicitly added to the Source of Truth and backend architecture later.





==================================================

35\. NO UNSUPPORTED STOCK TURNOVER

==================================================



Do NOT implement Stock Turnover simply because it appears in a visual reference.



If the existing backend/API does not provide a validated stock-turnover metric, it must not appear in the final frontend.



Do not invent a stock-turnover formula in React.





==================================================

36\. ANALYTICS API

==================================================



Use the existing backend endpoint:



GET /api/v1/analytics



The frontend should consume the existing response contract.



Do not create duplicate analytics endpoints.



Do not access Google Sheets directly from the frontend.





==================================================

37\. AI INSIGHT API

==================================================



Use the existing AI endpoint:



GET /api/v1/ai/insight



Use the existing backend response contract.



Do not create a separate AI analytics service in the frontend.





==================================================

38\. FRONTEND VS BACKEND RESPONSIBILITIES

==================================================



FRONTEND SHOULD:



\- display analytics metrics

\- display charts

\- display tables

\- provide supported date-range controls

\- format numbers and currencies

\- show trend labels supplied by backend

\- display historical information

\- display AI Insight

\- manage loading states

\- manage empty states

\- manage errors



FRONTEND MUST NOT:



\- calculate revenue

\- calculate cost

\- calculate profit

\- calculate margin

\- calculate inventory value

\- calculate demand metrics

\- classify demand trends

\- calculate stockout risk

\- calculate excess inventory

\- calculate reorder quantities

\- create forecasting models

\- create stock-turnover calculations

\- invent financial values

\- invent missing data

\- override backend recommendations





==================================================

39\. MISSING DATA

==================================================



Analytics must preserve backend missing-data semantics.



Important rules:



Missing sales ≠ zero sales.



Missing inventory ≠ zero inventory.



Missing cost ≠ zero cost.



Missing price ≠ zero price.



Missing shipment information ≠ no shipment.



Insufficient data should be displayed as:



\- unavailable

\- insufficient data

\- or another appropriate neutral state



Do not silently replace missing values with zero.





==================================================

40\. ZERO / DIVISION SAFETY

==================================================



The backend is responsible for safe calculations.



The frontend must correctly display:



\- zero revenue

\- zero units sold

\- zero demand

\- zero inventory



when these are valid values.



Do not convert valid zero values into unavailable.



Do not attempt calculations that could introduce divide-by-zero errors.





==================================================

41\. LOADING STATES

==================================================



While Analytics data is loading:



\- show lightweight chart skeletons

\- show metric-card skeletons

\- preserve the overall layout

\- avoid fake data



Do not display fabricated charts while waiting for the backend.





==================================================

42\. EMPTY STATES

==================================================



If there is insufficient analytics data:



Show a clear explanation.



Examples:



Not enough data for this period.



or:



No analytics available for the selected date range.



Do not fabricate trends.



If a specific metric cannot be calculated because required data is missing, only that metric should become unavailable where possible.





==================================================

43\. ERROR STATES

==================================================



If Analytics API requests fail:



\- show a clear user-friendly message

\- provide retry/refresh where appropriate

\- preserve the page structure



Do NOT expose:



\- stack traces

\- raw backend exceptions

\- credentials

\- API keys

\- internal infrastructure information





==================================================

44\. RESPONSIVE DESIGN

==================================================



Desktop is the primary MVP target.



On smaller screens:



\- sidebar may collapse

\- KPI cards may stack

\- charts may resize

\- tables may scroll horizontally

\- AI Insight should remain readable

\- date controls should remain usable



Do not create a completely separate mobile analytics experience.





==================================================

45\. VISUAL REFERENCE INTERPRETATION

==================================================



The Analytics visual references are design references only.



Use them to understand:



\- spacing

\- card layout

\- chart styling

\- typography

\- colors

\- visual hierarchy

\- AI section styling



Do NOT copy every component shown in the images.



In particular, if the reference image contains:



\- customer analytics

\- stock turnover

\- advanced forecasts

\- unsupported tabs

\- unsupported metrics

\- unsupported actions



do not implement them.



Backend/API/Source of Truth always wins.





==================================================

46\. ANALYTICS UX PRINCIPLE

==================================================



Analytics should help the owner understand their business without requiring them to be a data analyst.



The experience should feel like:



"What happened?"

→ "What is changing?"

→ "Where is it happening?"

→ "Why does it matter?"



The Inventory page handles detailed product actions.



The Analytics page handles understanding patterns and business performance.





==================================================

47\. ACCEPTANCE CRITERIA

==================================================



Overall:



\- \[ ] Analytics uses the approved InventoryIQ visual style.

\- \[ ] Sidebar matches the rest of the application.

\- \[ ] Analytics is clearly the active navigation item.

\- \[ ] Page header is present.

\- \[ ] Supported date-range control works correctly.

\- \[ ] Summary metrics come from the backend.

\- \[ ] Demand analytics are displayed correctly.

\- \[ ] Inventory analytics are displayed correctly.

\- \[ ] Financial analytics are displayed correctly when data is available.

\- \[ ] Historical trends use backend-provided data.

\- \[ ] Recent-vs-historical demand comparisons use backend results.

\- \[ ] No advanced forecasting is implemented.

\- \[ ] No customer analytics are implemented.

\- \[ ] No unsupported stock-turnover metric is implemented.

\- \[ ] No unsupported metrics are invented.

\- \[ ] Charts are simple and readable.

\- \[ ] Financial values are never fabricated.

\- \[ ] Missing data is not converted to zero.

\- \[ ] Valid zero values remain valid zero values.

\- \[ ] AI Insight is visually distinct with a subtle lavender treatment.

\- \[ ] AI Insight uses the existing backend AI endpoint.

\- \[ ] AI Insight is based on verified analytics context.

\- \[ ] Gemini does not calculate or override business logic.

\- \[ ] AI failure does not break Analytics.

\- \[ ] Loading state exists.

\- \[ ] Empty/insufficient-data state exists.

\- \[ ] Error state exists.

\- \[ ] No unsupported endpoints are created.

\- \[ ] No direct Google Sheets access occurs from the frontend.

\- \[ ] Analytics works with the realistic Cambodian mini-mart dataset.

\- \[ ] Analytics remains visually consistent with Dashboard and Inventory.





==================================================

48\. FINAL PRINCIPLE

==================================================



AnalyticsIQ should turn raw business data into information that a mini-mart owner can understand quickly.



Keep the experience focused:



Sales

→ Inventory

→ Financials

→ Historical Trends

→ Understand what changed

→ AI explains why it matters



The backend owns calculations.



The analytics engine owns the numbers.



The recommendation engine owns inventory decisions.



Gemini explains verified information.



The frontend presents everything clearly.



Do not add analytics features simply because they are common in larger BI platforms.

