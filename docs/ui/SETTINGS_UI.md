INVENTORYIQ — SETTINGS UI SPECIFICATION



==================================================

1\. SETTINGS SECTION PURPOSE

==================================================



The Settings section provides a lightweight place for the mini-mart owner to view and manage basic business information and the Google Sheets connection used by InventoryIQ.



The Settings section contains:



1\. Business Profile

2\. Google Sheets Connection



The page should remain intentionally simple.



Settings is NOT intended to become a large account-management or administration system.





==================================================

2\. IMPORTANT MVP SCOPE

==================================================



The current Settings MVP supports:



\- Business Profile

\- Google Sheets Connection

\- Connection/refresh state where supported



The current MVP does NOT include:



\- password management

\- account management

\- notification preferences

\- email preferences

\- weekly summaries

\- user management

\- roles/permissions

\- billing

\- subscriptions

\- danger zone

\- account deletion

\- product settings

\- inventory write-back settings

\- manual stock adjustment settings

\- advanced business configuration



Do NOT implement these features simply because they appear in generic SaaS settings designs.



Only implement functionality supported by the Source of Truth and backend contracts.





==================================================

3\. AUTHORITY ORDER

==================================================



When implementing Settings, use this authority order:



1\. InventoryIQ Source of Truth

2\. Backend API contracts

3\. This UI specification

4\. Visual reference image



The Source of Truth and backend define:



\- what settings exist

\- what values are valid

\- how settings are stored

\- what connection states mean

\- what actions are supported



The visual reference defines:



\- layout

\- spacing

\- typography

\- colors

\- card styling

\- visual hierarchy



If the visual reference contains unsupported settings or actions:



DO NOT IMPLEMENT THEM.





==================================================

4\. OVERALL VISUAL STYLE

==================================================



Use the established InventoryIQ visual language.



Settings should be:



\- clean

\- simple

\- modern

\- professional

\- lightweight

\- easy to understand



Use:



\- very light background

\- white cards

\- subtle borders

\- subtle shadows

\- modest rounded corners

\- dark navy text

\- blue primary actions

\- green connection/healthy states

\- red only for genuine errors or destructive states

\- simple outline icons

\- clean sans-serif typography



Settings should visually match:



\- Dashboard

\- Inventory

\- Analytics

\- Product Detail



Do not introduce a separate visual design system.





==================================================

5\. VISUAL REFERENCE: settings/main.png

==================================================



Reference:



docs/visual-references/settings/main.png



Use this image for:



\- overall Settings layout

\- sidebar

\- top navigation

\- page header

\- card structure

\- spacing

\- typography

\- section hierarchy

\- Google Sheets connection presentation



The visual reference contains several generic SaaS settings features that are NOT part of InventoryIQ.



Do NOT implement unsupported sections such as:



\- Account

\- Change Password

\- Notifications

\- Danger Zone

\- Sign Out

\- arbitrary preferences



The image is a visual reference, not a feature specification.





==================================================

6\. SETTINGS PAGE HEADER

==================================================



Page title:



Settings



Supporting text:



Manage your business profile and connected data.



Keep the header compact.



Do not add unnecessary explanatory text.





==================================================

7\. SETTINGS PAGE STRUCTURE

==================================================



The page should contain two primary cards/sections:



1\. Business Profile

2\. Google Sheets Connection



These should be clearly separated.



Business Profile should contain basic business information.



Google Sheets Connection should show the state of the data connection and supported connection/refresh information.





==================================================

8\. BUSINESS PROFILE

==================================================



Business Profile provides basic context about the business.



The profile should remain lightweight.



Potential supported fields include:



\- Business Name

\- Business Type

\- Currency

\- Timezone



Only use fields that are supported by the existing backend/configuration.



Do not invent additional business profile fields.





==================================================

9\. BUSINESS NAME

==================================================



Display the business name when available.



Example:



Coffee Corner



This is illustrative only.



Use the actual configured business name.



Do not hard-code "Coffee Corner" into production UI.





==================================================

10\. BUSINESS TYPE

==================================================



Display the configured business type when supported.



Example:



Mini-mart



or:



Food \& Beverage



Use actual configured data.



Do not invent business types.





==================================================

11\. CURRENCY

==================================================



Display the configured currency when supported.



Financial values elsewhere in the application should remain consistent with this currency.



Do not invent currency conversion.



Do not create exchange-rate functionality.





==================================================

12\. TIMEZONE

==================================================



Display the configured application/business timezone when supported.



InventoryIQ's current intended timezone is:



Asia/Phnom\_Penh



Use the backend/application configuration as the authoritative source.



Do not calculate a different timezone based on browser location.





==================================================

13\. BUSINESS PROFILE EDITING

==================================================



Only provide editing controls if the existing backend/API actually supports persistence for these settings.



Do NOT create a fake Save button that only changes browser state.



If the backend does not currently support business-profile writes:



\- display the information as read-only

\- do not invent a settings write endpoint



If business-profile persistence is added later, it must be implemented in the backend and added to the Source of Truth before the frontend adds editing functionality.





==================================================

14\. GOOGLE SHEETS CONNECTION

==================================================



The Google Sheets Connection section explains where InventoryIQ obtains its business data.



Conceptually:



Google Sheets

→ InventoryIQ backend

→ validation/processing

→ analytics/recommendations

→ frontend



The frontend should never directly access Google Sheets.



The backend owns the connection.





==================================================

15\. CONNECTION STATUS

==================================================



Show the current Google Sheets connection state supplied by the backend.



Possible states may include:



Connected



Unavailable



Not configured



Error



Use the backend's actual connection/availability state.



Do not assume that the presence of environment variables means the Google Sheet is definitely reachable.



Do not create frontend-only connection logic.





==================================================

16\. CONNECTED STATE

==================================================



When the backend reports a valid connected state:



Use a subtle green status indicator.



Example:



Connected



Supporting text:



Your inventory data is connected through Google Sheets.



Use actual backend information where available.



Do not fabricate sync times or account information.





==================================================

17\. UNAVAILABLE / NOT CONFIGURED STATE

==================================================



If the Google Sheets connection is not configured or unavailable:



Clearly communicate the state.



Examples:



Google Sheets not connected



or:



Connection unavailable



Explain the issue in simple language when the backend provides useful information.



Do not expose raw backend exceptions or infrastructure details.





==================================================

18\. REFRESH / SYNC

==================================================



Only provide a Sync/Refresh action if the existing backend API supports it.



The current architecture already supports fresh data reads through the backend.



Do not invent a separate synchronization system.



A refresh action should request fresh backend data rather than create an independent frontend cache.



Do not imply that a successful UI refresh means data was permanently synchronized if the backend does not provide that guarantee.





==================================================

19\. GOOGLE SHEETS WRITE-BACK

==================================================



IMPORTANT:



The current MVP does NOT support a general Google Sheets write-back system.



Do not add settings such as:



\- Enable two-way sync

\- Write changes to Sheets

\- Automatic sync configuration

\- Product sync settings

\- Inventory sync settings



The current product/inventory system should remain within the established MVP scope.



Manual stock adjustment is also NOT currently implemented.



Do not expose any setting that enables it.





==================================================

20\. DATA SOURCE INFORMATION

==================================================



The Settings page may show basic information about the connected Google Sheets source when the backend provides it.



Examples could include:



\- spreadsheet identifier/name

\- connection state

\- last successful read/refresh



Only display information that is actually available.



Do not expose:



\- service-account credentials

\- API keys

\- private tokens

\- raw configuration secrets





==================================================

21\. SECURITY

==================================================



Never display credentials in Settings.



Do NOT show:



\- Google service-account JSON

\- private keys

\- Gemini API keys

\- authentication tokens

\- environment variable values



Connection information should be descriptive, not secret-bearing.





==================================================

22\. LOADING STATE

==================================================



While Settings data is loading:



\- show lightweight skeletons

\- preserve the card structure

\- avoid fake business information



Do not show fake connection states while loading.





==================================================

23\. ERROR STATE

==================================================



If Settings data cannot be loaded:



\- show a clear user-friendly error

\- provide retry/refresh where appropriate

\- preserve the page structure



Do NOT expose:



\- raw exceptions

\- stack traces

\- credentials

\- API keys

\- internal infrastructure details





==================================================

24\. EMPTY / UNCONFIGURED STATE

==================================================



If business profile information is unavailable:



Show an appropriate unavailable state.



If Google Sheets is not configured:



Show a clear connection state explaining that the data source is not currently configured.



Do not fabricate a business profile.



Do not pretend the Google Sheet is connected.





==================================================

25\. FRONTEND VS BACKEND RESPONSIBILITIES

==================================================



FRONTEND SHOULD:



\- display business profile information

\- display Google Sheets connection state

\- display supported connection metadata

\- trigger supported refresh actions

\- format values

\- manage loading states

\- manage error states

\- manage unavailable states



FRONTEND MUST NOT:



\- directly access Google Sheets

\- determine connection health independently

\- create fake connection states

\- expose credentials

\- implement unsupported settings

\- invent settings endpoints

\- create a two-way sync system

\- implement manual stock adjustment

\- create product-management settings





==================================================

26\. SETTINGS API

==================================================



Use the existing backend Settings endpoint:



GET /api/v1/settings



Use the existing response contract.



Do not create duplicate settings endpoints.



The frontend communicates with FastAPI.



The frontend does not communicate directly with Google Sheets.





==================================================

27\. REFRESH BEHAVIOR

==================================================



When the user refreshes supported Settings/connection information:



\- request fresh backend state

\- update the displayed state

\- do not fabricate a successful connection

\- do not retain stale connection information when a newer backend response is available





==================================================

28\. RESPONSIVE DESIGN

==================================================



Desktop is the primary MVP target.



On smaller screens:



\- sidebar may collapse

\- Settings cards may stack vertically

\- connection information should remain readable

\- buttons should remain accessible

\- long values should wrap appropriately



Do not create a separate mobile Settings application.





==================================================

29\. VISUAL REFERENCE INTERPRETATION

==================================================



The Settings visual reference is a DESIGN REFERENCE ONLY.



Use it for:



\- layout

\- spacing

\- card hierarchy

\- typography

\- icons

\- connection-status presentation

\- general visual style



Do NOT copy unsupported functionality from the image.



Specifically, the following visible concepts in the reference are NOT current InventoryIQ MVP features:



\- Account settings

\- Change Password

\- Notifications

\- Weekly Summary

\- Product Insights notification settings

\- Danger Zone

\- Account deletion

\- arbitrary user preferences



Only Business Profile and Google Sheets Connection are currently relevant.





==================================================

30\. AI SETTINGS

==================================================



Do NOT create a separate AI settings section.



Gemini is part of the backend intelligence pipeline.



The user does not need to configure AI behavior through the Settings page in the current MVP.



Do not add:



\- AI model selector

\- AI prompt settings

\- AI creativity slider

\- AI preferences

\- AI chat settings

\- Gemini API key input



Gemini configuration is handled by the application/backend environment.





==================================================

31\. NOTIFICATION SETTINGS

==================================================



Do NOT implement notification settings.



The current MVP does not define:



\- email alerts

\- push notifications

\- SMS alerts

\- weekly email summaries

\- notification preferences



Do not add switches or settings for these features.





==================================================

32\. ACCOUNT SETTINGS

==================================================



Do NOT implement account management in the current Settings page.



Do not add:



\- password change

\- email change

\- account deletion

\- user roles

\- team management

\- profile photo management



These are outside current MVP scope.





==================================================

33\. MISSING DATA

==================================================



Preserve backend missing-data semantics.



Missing information should not be silently replaced with:



\- empty fake values

\- zeros

\- fake connection states

\- placeholder business names



Use appropriate unavailable states.





==================================================

34\. ACCEPTANCE CRITERIA

==================================================



The Settings page is complete only when:



\- \[ ] Settings follows the approved InventoryIQ visual style.

\- \[ ] Sidebar matches the rest of the application.

\- \[ ] Settings is clearly the active navigation item.

\- \[ ] Page header is present.

\- \[ ] Business Profile section exists.

\- \[ ] Business profile values come from supported backend/configuration data.

\- \[ ] Currency is displayed consistently when available.

\- \[ ] Timezone uses the application/backend configuration.

\- \[ ] No fake Save functionality is created.

\- \[ ] Google Sheets Connection section exists.

\- \[ ] Connection state comes from backend/application state.

\- \[ ] Connection status is visually clear.

\- \[ ] Refresh functionality is only shown if supported.

\- \[ ] No direct Google Sheets access occurs in the frontend.

\- \[ ] No credentials or secrets are exposed.

\- \[ ] No two-way sync settings are implemented.

\- \[ ] No manual stock adjustment settings are implemented.

\- \[ ] No product management settings are implemented.

\- \[ ] No notification settings are implemented.

\- \[ ] No account/password management is implemented.

\- \[ ] No billing/subscription settings are implemented.

\- \[ ] No unsupported endpoints are introduced.

\- \[ ] Loading state exists.

\- \[ ] Error state exists.

\- \[ ] Unconfigured/empty state exists.

\- \[ ] Settings remains visually consistent with Dashboard, Inventory, and Analytics.

\- \[ ] The page works with the realistic Cambodian mini-mart configuration.





==================================================

35\. FINAL PRINCIPLE

==================================================



Settings should be intentionally small.



The owner mainly needs to understand:



"What business is this?"



and:



"Is my data connection working?"



Keep the page focused:



Business Profile

→ Google Sheets Connection



Do not turn Settings into a generic SaaS administration panel.



Only expose functionality that InventoryIQ actually supports.

