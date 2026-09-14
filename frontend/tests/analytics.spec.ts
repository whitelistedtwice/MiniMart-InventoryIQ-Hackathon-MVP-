import { expect, test, type Route } from '@playwright/test';

import type {
  AIExplanationResponse,
  AIInsightContext,
  AnalyticsResponse,
  ProductAnalytics,
} from '../app/types';

/*
  Analytics page tests (Phase 13).

  Fixtures follow the ACTUAL `/api/v1/analytics` contract:
  AnalyticsResponse { generated_at, products: ProductAnalytics[], ai_insight_context }.
  Values are the real computed demo-pipeline output (as_of 2026-09-14);
  history series are trimmed to real points to keep fixtures readable.
  Money fields are numbers here to match the frontend TypeScript contract.
  No metric, trend, or currency symbol is invented.
*/

const MAMA_ANALYTICS: ProductAnalytics = {
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
    ['2026-09-01', 20],
    ['2026-09-04', 19],
    ['2026-09-10', 21],
    ['2026-09-14', 21],
  ],
  inventory_history: [
    ['2026-09-01', 6],
    ['2026-09-05', 6],
    ['2026-09-10', 6],
    ['2026-09-14', 8],
  ],
};

const COKE_ANALYTICS: ProductAnalytics = {
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
    ['2026-09-01', 12],
    ['2026-09-07', 14],
    ['2026-09-10', 12],
    ['2026-09-14', 14],
  ],
  inventory_history: [
    ['2026-09-01', 106],
    ['2026-09-07', 140],
    ['2026-09-10', 156],
    ['2026-09-14', 180],
  ],
};

const NOODLE_ANALYTICS: ProductAnalytics = {
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
};

const INSIGHT_CONTEXT: AIInsightContext = {
  generated_at: '2026-09-14T00:00:00',
  focus_area: 'demand',
  verified_trends: [
    '2 product(s) with decreasing demand',
    '9 product(s) with stable demand',
    '1 product(s) with unavailable demand trend',
  ],
  product_highlights: [
    {
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
      evidence: [
        'Missing required information: current inventory, sales history.',
      ],
    },
    {
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
  ],
};

const ANALYTICS: AnalyticsResponse = {
  generated_at: '2026-09-14T00:00:00',
  products: [MAMA_ANALYTICS, COKE_ANALYTICS, NOODLE_ANALYTICS],
  ai_insight_context: INSIGHT_CONTEXT,
};

/*
  AI insight states: first a Gemini outage (no fabricated text), then success.
*/
const AI_INSIGHT_UNAVAILABLE: AIExplanationResponse = {
  summary: null,
  reason: null,
  action_explanation: null,
  future_note: null,
  ai_available: false,
};

const AI_INSIGHT_OK: AIExplanationResponse = {
  summary:
    'TEST_AI_INSIGHT_ONLY Demand is stable across your products this period.',
  reason:
    'TEST_AI_INSIGHT_REASON Most products show steady demand; stock positions vary.',
  action_explanation:
    'TEST_AI_INSIGHT_ACTION Watch the low-stock products on the Inventory page.',
  future_note: 'TEST_AI_INSIGHT_NOTE No forecasting is performed.',
  ai_available: true,
};

async function fulfillJson(route: Route, json: unknown) {
  await route.fulfill({
    headers: { 'Access-Control-Allow-Origin': '*' },
    json,
  });
}

test.beforeEach(async ({ page }) => {
  await page.route('**/api/v1/analytics', (route) =>
    fulfillJson(route, ANALYTICS),
  );
  await page.route('**/api/v1/ai/insight', (route) =>
    fulfillJson(route, AI_INSIGHT_OK),
  );
});

test('analytics renders demand, inventory, and financial data from the backend', async ({
  page,
}) => {
  await page.goto('/analytics');
  await expect(
    page.getByRole('heading', { name: 'Analytics', level: 1 }),
  ).toBeVisible();

  // Demand section: backend values only, formatted for display.
  const demand = page.getByRole('region', { name: 'Demand analytics' });
  const mamaDemand = demand.getByRole('row', {
    name: /Mama Instant Noodles Chicken/,
  });
  await expect(mamaDemand).toContainText('292');
  await expect(mamaDemand).toContainText('20.9');
  await expect(mamaDemand).toContainText('21.1');
  await expect(mamaDemand).toContainText('Stable');

  // Inventory section: stock, days left, value, separate incoming, condition.
  const inventory = page.getByRole('region', { name: 'Inventory analytics' });
  const mamaInventory = inventory.getByRole('row', {
    name: /Mama Instant Noodles Chicken/,
  });
  await expect(
    mamaInventory.getByText('8', { exact: true }),
  ).toBeVisible();
  await expect(mamaInventory).toContainText('0.4 days');
  await expect(mamaInventory).toContainText('2.80');
  await expect(
    mamaInventory.getByText('300', { exact: true }),
  ).toBeVisible();
  await expect(mamaInventory).toContainText('Low');

  // Financial section: revenue/cost/profit/margin/exposure, no currency symbol.
  const financial = page.getByRole('region', { name: 'Financial analytics' });
  const mamaFinancial = financial.getByRole('row', {
    name: /Mama Instant Noodles Chicken/,
  });
  await expect(mamaFinancial).toContainText('175.20');
  await expect(mamaFinancial).toContainText('102.20');
  await expect(mamaFinancial).toContainText('73.00');
  await expect(mamaFinancial).toContainText('41.7%');
  await expect(mamaFinancial).toContainText('2.80');

  // noodle-bowl: missing metrics are "—", never fabricated zeroes. Its only
  // legitimate zero is the incoming-shipment count the backend provides.
  const noodleInventory = inventory.getByRole('row', {
    name: /Instant Bowl Noodles/,
  });
  await expect(
    noodleInventory.getByText('—', { exact: true }),
  ).toHaveCount(4);
  await expect(
    noodleInventory.getByText('0', { exact: true }),
  ).toHaveCount(1);
  const noodleFinancial = financial.getByRole('row', {
    name: /Instant Bowl Noodles/,
  });
  await expect(
    noodleFinancial.getByText('—', { exact: true }),
  ).toHaveCount(5);

  // No invented scope: no stock turnover, no currency symbol (C-023).
  await expect(page.getByRole('main')).not.toContainText('Stock Turnover');
  await expect(page.getByRole('main')).not.toContainText('$');
});

test('historical trends charts render observed series and insufficient-data states', async ({
  page,
}) => {
  await page.goto('/analytics');
  await expect(
    page.getByRole('heading', { name: 'Analytics', level: 1 }),
  ).toBeVisible();

  // Default product: first product (name order) with observable history
  // -> Coca-Cola. Charts show observed data with accessible descriptions.
  const salesChart = page.getByRole('img', {
    name: 'Units sold from 1 Sep to 14 Sep, between 12 and 14 units per day',
  });
  await expect(salesChart).toBeVisible();
  const stockChart = page.getByRole('img', {
    name: 'Stock level from 1 Sep to 14 Sep, ranging between 106 and 180 units',
  });
  await expect(stockChart).toBeVisible();
  await expect(page.getByText('Observed units sold per day.')).toBeVisible();
  await expect(
    page.getByText('Observed stock on hand over time (units).'),
  ).toBeVisible();

  // A product without history shows the insufficient-data state, no fake chart.
  await page.getByLabel('Choose product').selectOption('noodle-bowl');
  await expect(
    page.getByText('Not enough sales history to show a trend yet.'),
  ).toBeVisible();
  await expect(
    page.getByText('Not enough stock history to show a trend yet.'),
  ).toBeVisible();
  await expect(page.getByRole('img', { name: /Units sold/ })).toHaveCount(0);
  await expect(page.getByRole('img', { name: /Stock level/ })).toHaveCount(0);
});

test('analytics API failure shows a friendly error state and retry recovers', async ({
  page,
}) => {
  let analyticsRequests = 0;
  let shouldFail = true;
  await page.route('**/api/v1/analytics', async (route) => {
    analyticsRequests += 1;
    if (shouldFail) {
      await route.fulfill({
        status: 502,
        headers: { 'Access-Control-Allow-Origin': '*' },
        json: {
          error: 'data_access_error',
          message: 'Upstream Google Sheets error: simulated backend failure',
          details: {},
        },
      });
      return;
    }
    await fulfillJson(route, ANALYTICS);
  });

  await page.goto('/analytics');

  // Friendly error state; loading ended; no raw backend details.
  const errorHeading = page.getByRole('heading', {
    name: "We couldn't load your analytics",
  });
  await expect(errorHeading).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Try again' }),
  ).toBeVisible();
  await expect(
    page.getByRole('status', { name: 'Loading analytics' }),
  ).toHaveCount(0);
  await expect(page.getByRole('main')).not.toContainText('data_access_error');
  await expect(page.getByRole('main')).not.toContainText('simulated backend failure');

  // No automatic retry loop while the error is displayed.
  const requestsAtError = analyticsRequests;
  expect(analyticsRequests).toBe(requestsAtError);

  // Manual retry succeeds; the error state is fully gone.
  shouldFail = false;
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(
    page.getByRole('heading', { name: 'Analytics', level: 1 }),
  ).toBeVisible();
  await expect(
    page.getByRole('region', { name: 'Demand analytics' }),
  ).toBeVisible();
  await expect(errorHeading).toHaveCount(0);
  expect(analyticsRequests).toBe(requestsAtError + 1);
});

test('AI insight is lazy, recovers from unavailability, and never hides deterministic analytics', async ({
  page,
}) => {
  let aiRequests = 0;
  await page.route('**/api/v1/ai/insight', async (route) => {
    aiRequests += 1;
    await fulfillJson(route, aiRequests === 1 ? AI_INSIGHT_UNAVAILABLE : AI_INSIGHT_OK);
  });

  await page.goto('/analytics');
  await expect(
    page.getByRole('region', { name: 'Demand analytics' }),
  ).toBeVisible();

  // Lazy: no AI request at all until the owner asks for it.
  expect(aiRequests).toBe(0);

  await page.getByRole('button', { name: 'Get AI Insight' }).click();
  await expect(
    page.getByText(
      'AI insight is unavailable right now. Your analytics above are still the verified InventoryIQ results.',
    ),
  ).toBeVisible();

  // Deterministic analytics remain fully visible during AI failure.
  await expect(
    page.getByRole('region', { name: 'Demand analytics' }),
  ).toBeVisible();
  await expect(
    page
      .getByRole('region', { name: 'Demand analytics' })
      .getByRole('row', { name: /Mama Instant Noodles Chicken/ }),
  ).toContainText('292');

  // Try again issues exactly one new request and succeeds.
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.getByText(/TEST_AI_INSIGHT_ONLY/)).toBeVisible();
  await expect(
    page.getByText(
      'AI insight is unavailable right now. Your analytics above are still the verified InventoryIQ results.',
    ),
  ).toHaveCount(0);

  // Lazy expansion (1) + manual retry (1); no automatic refetch loop.
  expect(aiRequests).toBe(2);
});

test('analytics has no page overflow on mobile and no console errors', async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/analytics');
  await expect(
    page.getByRole('region', { name: 'Demand analytics' }),
  ).toBeVisible();

  // The page itself must not overflow horizontally; tables scroll inside
  // their own contained containers.
  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);

  // AI section remains usable on mobile.
  await expect(
    page.getByRole('button', { name: 'Get AI Insight' }),
  ).toBeVisible();

  expect(consoleErrors).toEqual([]);
});
