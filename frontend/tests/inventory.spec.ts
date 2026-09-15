import { expect, test, type Route } from '@playwright/test';

import type {
  AIExplanationResponse,
  ProductDetailResponse,
  ProductListItem,
  SettingsResponse,
} from '../app/types';

/*
  First real InventoryIQ E2E test: the Inventory list.

  The Inventory page is a pure display layer over GET /api/v1/inventory
  (contract: backend/app/contracts/api.py -> list[ProductListItem]). To keep
  the test deterministic and independent of Google Sheets credentials, the
  request is intercepted and fulfilled with the real demo dataset
  (backend/demo/cambodian_mini_mart.json), shaped exactly like the backend
  response and pre-sorted the way the backend sorts it (casefolded name).
  No UI logic is exercised that the backend does not already own.
*/

const INVENTORY: ProductListItem[] = [
  {
    product_id: 'angkor-beer',
    product_name: 'Angkor Beer 640ml / សៀរអង្គរ',
    category: 'Beverages',
    current_stock: 40,
    status: 'REORDER',
    days_remaining: 3.3136094674556213,
  },
  {
    product_id: 'sardines-155g',
    product_name: 'Canned Sardines 155g / ត្រីកោប៉ង់',
    category: 'Canned Goods',
    current_stock: 90,
    status: 'REDUCE EXCESS',
    days_remaining: 74.11764705882354,
  },
  {
    product_id: 'coke-330',
    product_name: 'Coca-Cola 330ml / កូកា',
    category: 'Beverages',
    current_stock: 180,
    status: 'NO ACTION',
    days_remaining: 13.404255319148936,
  },
  {
    product_id: 'water-1l',
    product_name: 'Drinking Water 1L / ទឹកសុទ្ធ',
    category: 'Beverages',
    current_stock: 300,
    status: 'NO ACTION',
    days_remaining: 10.824742268041236,
  },
  {
    product_id: 'eggs-10',
    product_name: 'Eggs (10 pcs) / ស៊ាងគោក្រហម',
    category: 'Fresh',
    current_stock: 25,
    status: 'MONITOR / PREPARE',
    days_remaining: 2.4647887323943665,
  },
  {
    product_id: 'rice-5kg',
    product_name: 'Fragrant Rice 5kg / អង្ករស្រួប 5kg',
    category: 'Dry Goods',
    current_stock: 120,
    status: 'NO ACTION',
    days_remaining: 43.07692307692308,
  },
  {
    product_id: 'noodle-bowl',
    product_name: 'Instant Bowl Noodles / មីចាន់',
    category: 'Instant Noodles',
    current_stock: null,
    status: 'UNAVAILABLE',
    days_remaining: null,
  },
  {
    product_id: 'detergent-1kg',
    product_name: 'Laundry Detergent 1kg / ម្សៅបោកខោស',
    category: 'Household',
    current_stock: 60,
    status: 'REDUCE EXCESS',
    days_remaining: 120,
  },
  {
    product_id: 'mama-chicken',
    product_name: 'Mama Instant Noodles Chicken / មីសួសម៉ាម៉ា',
    category: 'Instant Noodles',
    current_stock: 8,
    status: 'REORDER',
    days_remaining: 0.3835616438356164,
  },
  {
    product_id: 'shampoo-100ml',
    product_name: 'Shampoo Sachet 100ml / ស្បានជួតសក់',
    category: 'Personal Care',
    current_stock: 55,
    status: 'MONITOR / PREPARE',
    days_remaining: 14.528301886792454,
  },
  {
    product_id: 'soy-sauce',
    product_name: 'Soy Sauce 700ml / ទឹកស៊ីអ៊ួ',
    category: 'Condiments',
    current_stock: 85,
    status: 'MONITOR / PREPARE',
    days_remaining: 18.03030303030303,
  },
  {
    product_id: 'milk-1l',
    product_name: 'UHT Milk 1L / ទឹកដោះគោសុទ្ធ',
    category: 'Dairy',
    current_stock: 70,
    status: 'MONITOR / PREPARE',
    days_remaining: 12.25,
  },
];

/*
  Real Product Detail contract responses for the stale-state race tests.

  Values are the actual computed output of the real backend pipeline over
  backend/demo/cambodian_mini_mart.json (as_of 2026-09-14), captured via the
  FastAPI TestClient with the demo dependency seam. Money fields are numbers
  here to match the frontend's TypeScript contract.
*/

const MAMA_DETAIL: ProductDetailResponse = {
  product_id: 'mama-chicken',
  analytics: {
    product_id: 'mama-chicken',
    product_name: 'Mama Instant Noodles Chicken / មីសួសម៉ាម៉ា',
    demand: {
      total_sold: 292,
      average_daily_sales: 20.857142857142858,
      recent_daily_sales: 21.142857142857142,
      trend: 'stable',
    },
    inventory: {
      current_stock: 8,
      inventory_value: 2.8,
      days_of_stock_remaining: 0.3835616438356164,
      stock_status: 'low',
      stockout_risk: true,
      excess_units: 0,
      excess_value: 0,
    },
    shipment: {
      incoming_quantity: 300,
      expected_arrival: '2026-09-20',
      days_until_arrival: 6,
      expected_future_inventory: 308,
      stockout_before_arrival: true,
    },
    financial: {
      revenue: 175.2,
      estimated_cost: 102.2,
      profit: 73,
      profit_margin: 0.4166666666666667,
      financial_exposure: 2.8,
    },
    sales_history: [
      ['2026-09-01', 20], ['2026-09-02', 18], ['2026-09-03', 22], ['2026-09-04', 19],
      ['2026-09-05', 21], ['2026-09-06', 24], ['2026-09-07', 20], ['2026-09-08', 19],
      ['2026-09-09', 22], ['2026-09-10', 21], ['2026-09-11', 20], ['2026-09-12', 23],
      ['2026-09-13', 22], ['2026-09-14', 21],
    ],
    inventory_history: [
      ['2026-09-01', 6], ['2026-09-02', 3], ['2026-09-03', 4], ['2026-09-04', 3],
      ['2026-09-05', 6], ['2026-09-06', 6], ['2026-09-07', 8], ['2026-09-08', 5],
      ['2026-09-09', 7], ['2026-09-10', 6], ['2026-09-11', 8], ['2026-09-12', 6],
      ['2026-09-13', 7], ['2026-09-14', 8],
    ],
  },
  recommendation: {
    product_id: 'mama-chicken',
    product_name: 'Mama Instant Noodles Chicken / មីសួសម៉ាម៉ា',
    action: 'REORDER',
    priority: 1,
    reorder_quantity: 130,
    reorder_timing:
      'Order immediately - current stock may run out before the shipment arrives.',
    incoming_stock_sufficient: false,
    evidence: [
      'Stock covers about 0.4 days, but the next shipment arrives in 6 day(s).',
      'Order 130 units to reach 21 days of coverage (about 438 units).',
    ],
    current_stock: 8,
    incoming_quantity: 300,
    days_of_stock_remaining: 0.3835616438356164,
    days_until_arrival: 6,
    demand_trend: 'stable',
    target_stock_days: 21,
    excess_units: 0,
  },
  ai_context: {
    generated_at: '2026-09-14T00:00:00',
    product: {
      product_id: 'mama-chicken',
      product_name: 'Mama Instant Noodles Chicken / មីសួសម៉ាម៉ា',
      category: 'Instant Noodles',
      current_stock: 8,
      demand_trend: 'stable',
      average_daily_sales: 20.857142857142858,
      days_of_stock_remaining: 0.3835616438356164,
      incoming_quantity: 300,
      incoming_arrival_days: 6,
      recommendation_action: 'REORDER',
      priority: 1,
      recommended_reorder_quantity: 130,
      reorder_timing:
        'Order immediately - current stock may run out before the shipment arrives.',
      target_stock_days: 21,
      excess_units: 0,
      inventory_value: 2.8,
      financial_exposure: 2.8,
      evidence: [
        'Stock covers about 0.4 days, but the next shipment arrives in 6 day(s).',
        'Order 130 units to reach 21 days of coverage (about 438 units).',
      ],
    },
  },
  historical_inventory: [
    ['2026-09-01', 6], ['2026-09-02', 3], ['2026-09-03', 4], ['2026-09-04', 3],
    ['2026-09-05', 6], ['2026-09-06', 6], ['2026-09-07', 8], ['2026-09-08', 5],
    ['2026-09-09', 7], ['2026-09-10', 6], ['2026-09-11', 8], ['2026-09-12', 6],
    ['2026-09-13', 7], ['2026-09-14', 8],
  ],
};

const COKE_DETAIL: ProductDetailResponse = {
  product_id: 'coke-330',
  analytics: {
    product_id: 'coke-330',
    product_name: 'Coca-Cola 330ml / កូកា',
    demand: {
      total_sold: 188,
      average_daily_sales: 13.428571428571429,
      recent_daily_sales: 13.285714285714286,
      trend: 'stable',
    },
    inventory: {
      current_stock: 180,
      inventory_value: 90,
      days_of_stock_remaining: 13.404255319148936,
      stock_status: 'healthy',
      stockout_risk: false,
      excess_units: 0,
      excess_value: 0,
    },
    shipment: {
      incoming_quantity: 120,
      expected_arrival: '2026-09-16',
      days_until_arrival: 2,
      expected_future_inventory: 300,
      stockout_before_arrival: false,
    },
    financial: {
      revenue: 141,
      estimated_cost: 94,
      profit: 47,
      profit_margin: 0.3333333333333333,
      financial_exposure: 90,
    },
    sales_history: [
      ['2026-09-01', 12], ['2026-09-02', 14], ['2026-09-03', 11], ['2026-09-04', 13],
      ['2026-09-05', 15], ['2026-09-06', 16], ['2026-09-07', 14], ['2026-09-08', 12],
      ['2026-09-09', 13], ['2026-09-10', 12], ['2026-09-11', 14], ['2026-09-12', 13],
      ['2026-09-13', 15], ['2026-09-14', 14],
    ],
    inventory_history: [
      ['2026-09-01', 106], ['2026-09-02', 110], ['2026-09-03', 116], ['2026-09-04', 124],
      ['2026-09-05', 129], ['2026-09-06', 134], ['2026-09-07', 140], ['2026-09-08', 144],
      ['2026-09-09', 149], ['2026-09-10', 156], ['2026-09-11', 162], ['2026-09-12', 167],
      ['2026-09-13', 173], ['2026-09-14', 180],
    ],
  },
  recommendation: {
    product_id: 'coke-330',
    product_name: 'Coca-Cola 330ml / កូកា',
    action: 'NO ACTION',
    priority: 4,
    reorder_quantity: null,
    reorder_timing: null,
    incoming_stock_sufficient: true,
    evidence: [
      'Stock covers about 13.4 days, within the 14-day target.',
      'Demand is stable.',
      'No action needed.',
    ],
    current_stock: 180,
    incoming_quantity: 120,
    days_of_stock_remaining: 13.404255319148936,
    days_until_arrival: 2,
    demand_trend: 'stable',
    target_stock_days: 14,
    excess_units: 0,
  },
  ai_context: {
    generated_at: '2026-09-14T00:00:00',
    product: {
      product_id: 'coke-330',
      product_name: 'Coca-Cola 330ml / កូកា',
      category: 'Beverages',
      current_stock: 180,
      demand_trend: 'stable',
      average_daily_sales: 13.428571428571429,
      days_of_stock_remaining: 13.404255319148936,
      incoming_quantity: 120,
      incoming_arrival_days: 2,
      recommendation_action: 'NO ACTION',
      priority: 4,
      recommended_reorder_quantity: null,
      reorder_timing: null,
      target_stock_days: 14,
      excess_units: 0,
      inventory_value: 90,
      financial_exposure: 90,
      evidence: [
        'Stock covers about 13.4 days, within the 14-day target.',
        'Demand is stable.',
        'No action needed.',
      ],
    },
  },
  historical_inventory: [
    ['2026-09-01', 106], ['2026-09-02', 110], ['2026-09-03', 116], ['2026-09-04', 124],
    ['2026-09-05', 129], ['2026-09-06', 134], ['2026-09-07', 140], ['2026-09-08', 144],
    ['2026-09-09', 149], ['2026-09-10', 156], ['2026-09-11', 162], ['2026-09-12', 167],
    ['2026-09-13', 173], ['2026-09-14', 180],
  ],
};

/*
  Deterministic AI explanation fixtures for the stale-response race.
  Markers are test-only, unmistakable per product, and never production values.
*/
const AI_A: AIExplanationResponse = {
  summary: 'TEST_AI_PRODUCT_A_ONLY Mama Chicken AI summary.',
  reason: 'TEST_AI_PRODUCT_A_REASON why this recommendation.',
  action_explanation: 'TEST_AI_PRODUCT_A_ACTION recommended action.',
  future_note: 'TEST_AI_PRODUCT_A_NOTE additional context.',
  ai_available: true,
};

const AI_B: AIExplanationResponse = {
  summary: 'TEST_AI_PRODUCT_B_ONLY Coca-Cola AI summary.',
  reason: 'TEST_AI_PRODUCT_B_REASON why this recommendation.',
  action_explanation: 'TEST_AI_PRODUCT_B_ACTION recommended action.',
  future_note: 'TEST_AI_PRODUCT_B_NOTE additional context.',
  ai_available: true,
};

/*
  Real noodle-bowl detail: a product with missing inventory and sales data.
  Every unavailable metric is null (never zero), and the recommendation is
  UNAVAILABLE with a missing-data evidence line.
*/
const NOODLE_DETAIL: ProductDetailResponse = {
  product_id: 'noodle-bowl',
  analytics: {
    product_id: 'noodle-bowl',
    product_name: 'Instant Bowl Noodles / មីចាន់',
    demand: {
      total_sold: null,
      average_daily_sales: null,
      recent_daily_sales: null,
      trend: 'unavailable',
    },
    inventory: {
      current_stock: null,
      inventory_value: null,
      days_of_stock_remaining: null,
      stock_status: null,
      stockout_risk: null,
      excess_units: null,
      excess_value: null,
    },
    shipment: {
      incoming_quantity: 0,
      expected_arrival: null,
      days_until_arrival: null,
      expected_future_inventory: null,
      stockout_before_arrival: null,
    },
    financial: {
      revenue: null,
      estimated_cost: null,
      profit: null,
      profit_margin: null,
      financial_exposure: null,
    },
    sales_history: [],
    inventory_history: [],
  },
  recommendation: {
    product_id: 'noodle-bowl',
    product_name: 'Instant Bowl Noodles / មីចាន់',
    action: 'UNAVAILABLE',
    priority: 0,
    reorder_quantity: null,
    reorder_timing: null,
    incoming_stock_sufficient: null,
    evidence: ['Missing required information: current inventory, sales history.'],
    current_stock: null,
    incoming_quantity: 0,
    days_of_stock_remaining: null,
    days_until_arrival: null,
    demand_trend: 'unavailable',
    target_stock_days: 21,
    excess_units: null,
  },
  ai_context: {
    generated_at: '2026-09-14T00:00:00',
    product: {
      product_id: 'noodle-bowl',
      product_name: 'Instant Bowl Noodles / មីចាន់',
      category: 'Instant Noodles',
      current_stock: null,
      demand_trend: 'unavailable',
      average_daily_sales: null,
      days_of_stock_remaining: null,
      incoming_quantity: 0,
      incoming_arrival_days: null,
      recommendation_action: 'UNAVAILABLE',
      priority: 0,
      recommended_reorder_quantity: null,
      reorder_timing: null,
      target_stock_days: 21,
      excess_units: null,
      inventory_value: null,
      financial_exposure: null,
      evidence: ['Missing required information: current inventory, sales history.'],
    },
  },
  historical_inventory: [],
};

/*
  AI lazy-loading states: the first response simulates a Gemini outage
  (ai_available: false, no fabricated text); the retry succeeds.
*/
const AI_UNAVAILABLE: AIExplanationResponse = {
  summary: null,
  reason: null,
  action_explanation: null,
  future_note: null,
  ai_available: false,
};

const AI_MAMA_OK: AIExplanationResponse = {
  summary:
    'Reorder 130 units of Mama Instant Noodles now: stock covers under a day and the next shipment may arrive too late.',
  reason: 'Stock covers about 0.4 days, but the next shipment arrives in 6 day(s).',
  action_explanation: 'Reorder 130 units to reach 21 days of coverage.',
  future_note: 'Watch the shipment expected on 20 Sep 2026.',
  ai_available: true,
};

/*
  Shared settings response (Phase 15). The app shell fetches settings once
  per load for the business profile; no currency is configured here so money
  rendering stays plain in these tests.
*/
const SETTINGS: SettingsResponse = {
  business_name: "Chen's Mini-Mart",
  business_type: 'Mini-mart',
  currency: null,
  timezone: 'Asia/Phnom_Penh',
  sheets_connected: false,
  sheets_connection_state: 'not_configured',
  sheets_connection_error: null,
  sheets_last_checked_at: null,
  last_sync_at: null,
};

/** Fulfill a cross-origin request; the CORS header mirrors the backend. */
async function fulfillJson(route: Route, json: unknown) {
  await route.fulfill({
    headers: { 'Access-Control-Allow-Origin': '*' },
    json,
  });
}

/** Shared fulfillment: the exact demo dataset over the real API contract. */
async function fulfillInventory(route: Route) {
  await fulfillJson(route, INVENTORY);
}

test.beforeEach(async ({ page }) => {
  // Intercept the cross-origin backend calls; the CORS header mimics the
  // backend's real CORS behaviour for the localhost frontend origin.
  await page.route('**/api/v1/settings', (route) =>
    fulfillJson(route, SETTINGS),
  );
  await page.route('**/api/v1/inventory', fulfillInventory);
});

test('inventory list renders demo products and search filters them', async ({
  page,
}) => {
  // Open /inventory and verify the page renders.
  await page.goto('/inventory');
  await expect(
    page.getByRole('heading', { name: 'Inventory', level: 1 }),
  ).toBeVisible();

  // Products are displayed (the full 12-product demo list).
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();
  const angkorRow = page.getByRole('row', { name: /Angkor Beer 640ml/ });
  await expect(angkorRow).toBeVisible();
  await expect(angkorRow).toContainText('Beverages');
  await expect(angkorRow).toContainText('Reorder');

  // The Inventory search field exists. There is also a top-bar search
  // (both labelled "Search products"), so the page field is identified by
  // its exact placeholder "Search products…" vs "Search products, categories…".
  const search = page.getByPlaceholder('Search products…', { exact: true });
  await expect(search).toBeVisible();

  // Enter the search term.
  await search.fill('angkor');

  // The filtered result matches the demo data and reports the expected count.
  await expect(page.getByText('Showing 1 of 12 products')).toBeVisible();
  await expect(
    angkorRow.getByText('40', { exact: true }),
  ).toBeVisible();

  // Unrelated products are not displayed as matching results.
  await expect(page.getByRole('row', { name: /Coca-Cola/ })).toHaveCount(0);
  await expect(page.getByRole('row', { name: /Mama Instant Noodles/ })).toHaveCount(
    0,
  );
  await expect(page.getByRole('row', { name: /Drinking Water/ })).toHaveCount(0);
});

test('search with no matches shows the empty state, not an error', async ({
  page,
}) => {
  // Open /inventory and wait for the mocked demo list to render.
  await page.goto('/inventory');
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();

  // The authoritative Inventory-page search field.
  const search = page.getByPlaceholder('Search products…', { exact: true });
  await expect(search).toBeVisible();

  // Search for a term that does not exist in the demo data.
  await search.fill('zzzz');

  // The input keeps the term and the count reports zero matching products.
  await expect(search).toHaveValue('zzzz');
  await expect(page.getByText('Showing 0 of 12 products')).toBeVisible();

  // The empty state replaces the table and explains that nothing matched.
  await expect(
    page.getByRole('heading', { name: 'No products found', level: 2 }),
  ).toBeVisible();
  await expect(
    page.getByText(
      'No products match your search or filters. Try a different term or clear the filters.',
    ),
  ).toBeVisible();

  // No product rows are displayed (the whole table is unmounted).
  await expect(page.getByRole('table')).toHaveCount(0);

  // The page remains structurally usable and shows no error state.
  await expect(search).toBeVisible();
  await expect(search).toBeEditable();
  await expect(
    page.getByRole('heading', { name: 'Inventory', level: 1 }),
  ).toBeVisible();
  await expect(
    page.getByRole('heading', { name: "We couldn't load your inventory" }),
  ).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Try again' })).toHaveCount(0);
});

test('shows the loading state while the inventory request is pending', async ({
  page,
}) => {
  // Hold the inventory response until the test releases it, so the loading
  // state is asserted while the request is genuinely pending.
  let releaseInventory!: () => void;
  const inventoryHeld = new Promise<void>((resolve) => {
    releaseInventory = resolve;
  });

  // Request audit: count inventory requests and capture every request that
  // leaves the app origin (the frontend only calls the FastAPI backend).
  let inventoryRequests = 0;
  const nonAppRequests: string[] = [];
  page.on('request', (request) => {
    if (!request.url().startsWith('http://localhost:3000')) {
      nonAppRequests.push(request.url());
    }
  });

  // Overrides the beforeEach route (later registrations are tried first)
  // so the identical fulfillment happens only after the hold is released.
  await page.route('**/api/v1/inventory', async (route) => {
    inventoryRequests += 1;
    await inventoryHeld;
    await fulfillInventory(route);
  });

  // Prove the page actually issues the inventory request and that it is
  // held pending (not merely slow).
  const inventoryRequest = page.waitForRequest('**/api/v1/inventory');
  await page.goto('/inventory');
  await inventoryRequest;

  // While the request is pending: the loading skeleton is shown, and the
  // page does not present data, an empty state, or an error state.
  const loading = page.getByRole('status', { name: 'Loading inventory' });
  await expect(loading).toBeVisible();
  await expect(page.getByRole('table')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: 'No products yet' })).toHaveCount(
    0,
  );
  await expect(
    page.getByRole('heading', { name: 'No products found' }),
  ).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: "We couldn't load your inventory" }),
  ).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Try again' })).toHaveCount(0);

  // Release the held response; the page transitions to the loaded state.
  releaseInventory();
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();
  await expect(page.getByRole('row', { name: /Angkor Beer 640ml/ })).toBeVisible();

  // The loading state is gone and no error appeared.
  await expect(loading).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: "We couldn't load your inventory" }),
  ).toHaveCount(0);

  // The page really did request the inventory data before rendering it.
  expect(inventoryRequests).toBeGreaterThanOrEqual(1);
});

test('shows the friendly error state when the inventory request fails, then recovers on retry', async ({
  page,
}) => {
  // The documented backend failure for this endpoint (CONCERNS.md C-021):
  // a Google Sheets read failure surfaces as HTTP 502 with the real
  // ApiError envelope ("data_access_error"). This exercises apiGet's
  // non-2xx path, which maps to the UI's friendly "server" error message.
  let inventoryRequests = 0;
  let shouldFail = true;
  await page.route('**/api/v1/inventory', async (route) => {
    inventoryRequests += 1;
    if (!shouldFail) {
      await fulfillInventory(route);
      return;
    }
    await route.fulfill({
      status: 502,
      headers: { 'Access-Control-Allow-Origin': '*' },
      json: {
        error: 'data_access_error',
        message: 'Upstream Google Sheets error: simulated backend failure',
        details: {},
      },
    });
  });

  // Prove the failed request actually occurs before the error state.
  const inventoryRequest = page.waitForRequest('**/api/v1/inventory');
  await page.goto('/inventory');
  await inventoryRequest;

  // Loading ends and the friendly error state appears.
  const errorHeading = page.getByRole('heading', {
    name: "We couldn't load your inventory",
  });
  await expect(errorHeading).toBeVisible();
  await expect(
    page.getByText(
      "The server couldn't load your inventory right now. Please try again.",
    ),
  ).toBeVisible();
  const tryAgain = page.getByRole('button', { name: 'Try again' });
  await expect(tryAgain).toBeVisible();

  // The loading skeleton is gone; no product or empty state is shown.
  await expect(
    page.getByRole('status', { name: 'Loading inventory' }),
  ).toHaveCount(0);
  await expect(page.getByRole('table')).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: 'No products yet' }),
  ).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: 'No products found' }),
  ).toHaveCount(0);

  // The Inventory page shell is still intact.
  await expect(
    page.getByRole('heading', { name: 'Inventory', level: 1 }),
  ).toBeVisible();

  // Raw backend/internal details are never displayed — client.ts uses
  // fixed friendly messages and never surfaces the response body.
  const main = page.getByRole('main');
  await expect(main).not.toContainText('data_access_error');
  await expect(main).not.toContainText('simulated backend failure');
  await expect(main).not.toContainText('GOOGLE_SHEET_ID');
  await expect(main).not.toContainText('Traceback');

  // No unintended automatic retry: the request count is stable across the
  // error-state assertions above (only the initial StrictMode batch).
  const requestsAtError = inventoryRequests;
  expect(inventoryRequests).toBe(requestsAtError);

  // Retry: the next request succeeds with the shared demo dataset.
  shouldFail = false;
  await tryAgain.click();
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();
  await expect(page.getByRole('row', { name: /Angkor Beer 640ml/ })).toBeVisible();

  // The error state is fully gone after a successful retry.
  await expect(errorHeading).toHaveCount(0);
  await expect(tryAgain).toHaveCount(0);

  // Exactly one additional request happened for the manual retry
  // (StrictMode double-invocation applies only to the initial mount).
  expect(inventoryRequests).toBe(requestsAtError + 1);
});

test('switching from product A to product B never shows stale product A detail data', async ({
  page,
}) => {
  // Hold B's detail response so the transition can be observed while B is
  // genuinely pending.
  let releaseB!: () => void;
  const bHeld = new Promise<void>((resolve) => {
    releaseB = resolve;
  });

  await page.route('**/api/v1/inventory/*', async (route) => {
    const url = route.request().url();
    if (url.endsWith('/mama-chicken')) {
      await fulfillJson(route, MAMA_DETAIL);
    } else if (url.endsWith('/coke-330')) {
      await bHeld;
      await fulfillJson(route, COKE_DETAIL);
    } else {
      await route.fallback();
    }
  });

  // Product A loads fully with its own identity and values.
  await page.goto('/inventory/mama-chicken');
  const aHeading = page.getByRole('heading', {
    level: 1,
    name: /Mama Instant Noodles Chicken/,
  });
  await expect(aHeading).toBeVisible();
  await expect(page.getByText('Reorder 130 units')).toBeVisible();
  await expect(
    page.getByRole('img', { name: /ranging between 3 and 8 units/ }),
  ).toBeVisible();

  // Switch to product B through the real UI: list, then B's row link.
  await page.getByRole('link', { name: 'Back to Inventory' }).click();
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();

  const bDetailRequest = page.waitForRequest('**/api/v1/inventory/coke-330');
  await page.getByRole('link', { name: /Coca-Cola 330ml/ }).click();
  await bDetailRequest;

  // While B's detail is held pending: a generic skeleton is shown, and none
  // of A's identity/data is presented as if it belongs to B.
  await expect(
    page.getByRole('status', { name: 'Loading product' }),
  ).toBeVisible();
  await expect(aHeading).toHaveCount(0);
  await expect(page.getByText('Reorder 130 units')).toHaveCount(0);
  await expect(
    page.getByRole('img', { name: /ranging between 3 and 8 units/ }),
  ).toHaveCount(0);
  await expect(
    page.getByRole('heading', { level: 1, name: /Coca-Cola 330ml/ }),
  ).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: "We couldn't load this product" }),
  ).toHaveCount(0);

  // Release B's response: B renders correctly, A never reappears.
  releaseB();
  const bHeading = page.getByRole('heading', {
    level: 1,
    name: /Coca-Cola 330ml/,
  });
  await expect(bHeading).toBeVisible();
  await expect(page.getByText('No action needed', { exact: true })).toBeVisible();
  await expect(
    page.getByRole('img', { name: /ranging between 106 and 180 units/ }),
  ).toBeVisible();
  await expect(
    page.getByRole('status', { name: 'Loading product' }),
  ).toHaveCount(0);
  await expect(aHeading).toHaveCount(0);
  await expect(page.getByText('Reorder 130 units')).toHaveCount(0);
});

test('a late AI response from product A cannot overwrite product B AI insight', async ({
  page,
}) => {
  // A's AI response is held; it is delivered only after B is fully active.
  let releaseAAi!: () => void;
  const aAiHeld = new Promise<void>((resolve) => {
    releaseAAi = resolve;
  });
  let markADelivered!: () => void;
  const aAiDelivered = new Promise<void>((resolve) => {
    markADelivered = resolve;
  });

  let aAiRequests = 0;
  let bAiRequests = 0;

  await page.route('**/api/v1/inventory/*', async (route) => {
    const url = route.request().url();
    if (url.endsWith('/mama-chicken')) {
      await fulfillJson(route, MAMA_DETAIL);
    } else if (url.endsWith('/coke-330')) {
      await fulfillJson(route, COKE_DETAIL);
    } else {
      await route.fallback();
    }
  });

  await page.route('**/api/v1/ai/recommendation/*', async (route) => {
    const url = route.request().url();
    if (url.endsWith('/mama-chicken')) {
      aAiRequests += 1;
      await aAiHeld;
      await fulfillJson(route, AI_A);
      markADelivered();
    } else if (url.endsWith('/coke-330')) {
      bAiRequests += 1;
      await fulfillJson(route, AI_B);
    } else {
      await route.fallback();
    }
  });

  // 1. Product A detail loads; A's AI is lazy until expanded.
  await page.goto('/inventory/mama-chicken');
  await expect(
    page.getByRole('heading', {
      level: 1,
      name: /Mama Instant Noodles Chicken/,
    }),
  ).toBeVisible();
  await expect(page.getByText('Reorder 130 units')).toBeVisible();

  // 2. Expand A's AI insight and confirm its request fires (held pending).
  const aAiRequest = page.waitForRequest(
    '**/api/v1/ai/recommendation/mama-chicken',
  );
  await page.getByRole('button', { name: 'See What AI Recommends' }).click();
  await aAiRequest;

  // 3. While A's AI is still pending, switch to B through the real UI.
  await page.getByRole('link', { name: 'Back to Inventory' }).click();
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();
  await page.getByRole('link', { name: /Coca-Cola 330ml/ }).click();
  const bHeading = page.getByRole('heading', {
    level: 1,
    name: /Coca-Cola 330ml/,
  });
  await expect(bHeading).toBeVisible();

  // 4. Open B's AI insight; its deterministic response resolves immediately.
  await page.getByRole('button', { name: 'See What AI Recommends' }).click();
  await expect(page.getByText(/TEST_AI_PRODUCT_B_ONLY/)).toBeVisible();
  await expect(page.getByText(/TEST_AI_PRODUCT_B_REASON/)).toBeVisible();

  // 5. Deliver A's long-pending response now that B is already displayed.
  releaseAAi();
  await aAiDelivered;

  // 6. B's AI panel is unchanged; A's late content appears nowhere.
  await expect(page.getByText(/TEST_AI_PRODUCT_B_ONLY/)).toBeVisible();
  await expect(page.getByText(/TEST_AI_PRODUCT_B_REASON/)).toBeVisible();
  await expect(page.getByText(/TEST_AI_PRODUCT_A_ONLY/)).toHaveCount(0);
  await expect(page.getByText(/TEST_AI_PRODUCT_A_REASON/)).toHaveCount(0);
  await expect(page.getByText(/TEST_AI_PRODUCT_A_ACTION/)).toHaveCount(0);
  await expect(page.getByText(/TEST_AI_PRODUCT_A_NOTE/)).toHaveCount(0);
  await expect(bHeading).toBeVisible();
  await expect(page.getByText('No action needed', { exact: true })).toBeVisible();
  await expect(
    page.getByRole('heading', {
      level: 1,
      name: /Mama Instant Noodles Chicken/,
    }),
  ).toHaveCount(0);
  await expect(page.getByText('Reorder 130 units')).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: "We couldn't load this product" }),
  ).toHaveCount(0);

  // Exactly one lazy AI request per product; no retries or loops.
  expect(aAiRequests).toBe(1);
  expect(bAiRequests).toBe(1);
});

test('filters narrow the product list by category, status, and combined search', async ({
  page,
}) => {
  await page.goto('/inventory');
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();

  // Category filter: Instant Noodles -> mama-chicken + noodle-bowl.
  await page.getByLabel('Filter by category').selectOption('Instant Noodles');
  await expect(page.getByText('Showing 2 of 12 products')).toBeVisible();
  await expect(
    page.getByRole('row', { name: /Mama Instant Noodles Chicken/ }),
  ).toBeVisible();
  await expect(page.getByRole('row', { name: /Instant Bowl Noodles/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Coca-Cola/ })).toHaveCount(0);

  // Status filter on its own: REORDER -> angkor-beer + mama-chicken.
  await page.getByLabel('Filter by category').selectOption('all');
  await page.getByLabel('Filter by status').selectOption('REORDER');
  await expect(page.getByText('Showing 2 of 12 products')).toBeVisible();
  await expect(page.getByRole('row', { name: /Angkor Beer 640ml/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Coca-Cola/ })).toHaveCount(0);

  // Filters compose with search: Instant Noodles + REORDER -> mama only.
  await page.getByLabel('Filter by category').selectOption('Instant Noodles');
  await expect(page.getByText('Showing 1 of 12 products')).toBeVisible();
  await expect(
    page.getByRole('row', { name: /Mama Instant Noodles Chicken/ }),
  ).toBeVisible();
  await expect(page.getByRole('row', { name: /Instant Bowl Noodles/ })).toHaveCount(
    0,
  );

  // Search + filter with no intersection shows the filtered empty state.
  const search = page.getByPlaceholder('Search products…', { exact: true });
  await search.fill('angkor');
  await expect(page.getByText('Showing 0 of 12 products')).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'No products found', level: 2 }),
  ).toBeVisible();
});

test('inventory list renders all five statuses and missing values as em dashes', async ({
  page,
}) => {
  await page.goto('/inventory');
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();

  // All five backend statuses are represented (real demo data):
  // REORDER x2, REDUCE EXCESS x2, MONITOR / PREPARE x4, NO ACTION x3,
  // UNAVAILABLE x1. Badge labels are presentation-only mappings.
  await expect(page.getByText('Reorder', { exact: true })).toHaveCount(2);
  await expect(page.getByText('Reduce Excess', { exact: true })).toHaveCount(2);
  await expect(page.getByText('Monitor / Prepare', { exact: true })).toHaveCount(4);
  await expect(page.getByText('No Action', { exact: true })).toHaveCount(3);
  await expect(page.getByText('Unavailable', { exact: true })).toHaveCount(1);

  // noodle-bowl has no inventory snapshot: missing values render "—",
  // never a fabricated zero.
  const bowlRow = page.getByRole('row', { name: /Instant Bowl Noodles/ });
  await expect(bowlRow).toContainText('—');
  await expect(bowlRow).not.toContainText('0');
});

test('product detail shows missing data as unavailable, not zero', async ({
  page,
}) => {
  await page.route('**/api/v1/inventory/noodle-bowl', (route) =>
    fulfillJson(route, NOODLE_DETAIL),
  );
  await page.goto('/inventory/noodle-bowl');

  await expect(
    page.getByRole('heading', {
      level: 1,
      name: /Instant Bowl Noodles/,
    }),
  ).toBeVisible();

  // Status and missing metrics: "—", never fabricated zeroes. The exact
  // text "Unavailable" appears twice: the status badge and the demand trend.
  await expect(page.getByText('Unavailable', { exact: true })).toHaveCount(2);
  await expect(page.getByText('— left')).toBeVisible();
  await expect(page.getByText('Not enough data for a recommendation')).toBeVisible();

  // The real missing-data evidence line from the backend.
  await expect(
    page.getByText(
      'Missing required information: current inventory, sales history.',
    ),
  ).toBeVisible();

  // No fake chart and no fake incoming shipment.
  await expect(
    page.getByText('Not enough stock history to show a trend yet.'),
  ).toBeVisible();
  await expect(page.getByText('No incoming shipment for this product.')).toBeVisible();

  // Product Details card: unavailable metrics are "—", provided ones shown.
  const detailsCard = page
    .getByRole('heading', { name: 'Product Details' })
    .locator('..');
  await expect(detailsCard).toContainText('Instant Noodles');
  await expect(detailsCard).toContainText('Unavailable');
  await expect(detailsCard).toContainText('—');
  await expect(detailsCard).toContainText('21 days');
  await expect(detailsCard).not.toContainText('0');
});

test('AI unavailable shows a friendly fallback and Try again recovers', async ({
  page,
}) => {
  let aiRequests = 0;
  await page.route('**/api/v1/inventory/mama-chicken', (route) =>
    fulfillJson(route, MAMA_DETAIL),
  );
  await page.route('**/api/v1/ai/recommendation/mama-chicken', async (route) => {
    aiRequests += 1;
    await fulfillJson(route, aiRequests === 1 ? AI_UNAVAILABLE : AI_MAMA_OK);
  });

  await page.goto('/inventory/mama-chicken');
  await expect(
    page.getByRole('heading', {
      level: 1,
      name: /Mama Instant Noodles Chicken/,
    }),
  ).toBeVisible();

  // Lazy: expand the AI insight; the first response is a Gemini outage.
  await page.getByRole('button', { name: 'See What AI Recommends' }).click();
  await expect(
    page.getByText(
      'AI insight is unavailable right now. The recommendation above is still the verified InventoryIQ result.',
    ),
  ).toBeVisible();

  // The deterministic recommendation survives the AI failure.
  await expect(page.getByText('Reorder 130 units')).toBeVisible();

  // Try again issues exactly one new request and succeeds.
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.getByText(/Reorder 130 units of Mama Instant Noodles now/)).toBeVisible();
  await expect(
    page.getByText(
      'AI insight is unavailable right now. The recommendation above is still the verified InventoryIQ result.',
    ),
  ).toHaveCount(0);

  // Lazy expansion (1) + manual retry (1); no automatic refetch loop.
  expect(aiRequests).toBe(2);
});

test('global search routes the query into the inventory list search', async ({
  page,
}) => {
  // C-022: the top-bar search is not an independent search state; it
  // navigates to Inventory with the query, which the page then applies.
  await page.goto('/inventory');
  await expect(page.getByText('Showing 12 of 12 products')).toBeVisible();

  const globalSearch = page.getByPlaceholder('Search products, categories…');
  await globalSearch.fill('angkor');
  await globalSearch.press('Enter');

  await expect(page).toHaveURL(/\/inventory\?q=angkor$/);
  const pageSearch = page.getByPlaceholder('Search products…', { exact: true });
  await expect(pageSearch).toHaveValue('angkor');
  await expect(page.getByText('Showing 1 of 12 products')).toBeVisible();
  await expect(page.getByRole('row', { name: /Angkor Beer 640ml/ })).toBeVisible();
  await expect(page.getByRole('row', { name: /Coca-Cola/ })).toHaveCount(0);
});
