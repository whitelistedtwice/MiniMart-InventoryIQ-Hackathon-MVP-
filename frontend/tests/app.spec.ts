import { expect, test, type Route } from '@playwright/test';

import type {
  AIExplanationResponse,
  AnalyticsResponse,
  DashboardResponse,
  ProductDetailResponse,
  ProductListItem,
  SettingsResponse,
} from '../app/types';

/*
  Phase 15 cross-page consistency suite.

  These tests verify that the four pages behave like ONE product:

  - the shell shows the configured business name (and a safe fallback);
  - navigation works through Dashboard -> Inventory -> Analytics -> Settings;
  - money is formatted in exactly one configured currency everywhere, and
    without a currency when none is configured;
  - no backend secret reaches the browser;
  - mobile navigation has no page-level horizontal overflow.

  Fixtures are the real computed output of the demo pipeline
  (backend/demo/cambodian_mini_mart.json, as_of 2026-09-14) over the actual
  API contracts. Histories are trimmed to real points for readability.
*/

const SETTINGS: SettingsResponse = {
  business_name: "Chen's Mini-Mart",
  business_type: 'Mini-mart',
  currency: 'USD',
  timezone: 'Asia/Phnom_Penh',
  sheets_connected: true,
  last_sync_at: '2026-09-14T08:30:00',
};

const ANGKOR: ProductListItem = {
  product_id: 'angkor-beer',
  product_name: 'Angkor Beer 640ml / សៀរអង្គរ',
  category: 'Beverages',
  current_stock: 40,
  status: 'REORDER',
  days_remaining: 3.3136094674556213,
};

const COKE: ProductListItem = {
  product_id: 'coke-330',
  product_name: 'Coca-Cola 330ml / កូកា',
  category: 'Beverages',
  current_stock: 180,
  status: 'NO ACTION',
  days_remaining: 13.404255319148936,
};

const NOODLE: ProductListItem = {
  product_id: 'noodle-bowl',
  product_name: 'Instant Bowl Noodles / មីចាន់',
  category: 'Instant Noodles',
  current_stock: null,
  status: 'UNAVAILABLE',
  days_remaining: null,
};

const MAMA: ProductListItem = {
  product_id: 'mama-chicken',
  product_name: 'Mama Instant Noodles Chicken / មីសួសម៉ាម៉ា',
  category: 'Instant Noodles',
  current_stock: 8,
  status: 'REORDER',
  days_remaining: 0.3835616438356164,
};

// Backend order: casefolded product name.
const INVENTORY: ProductListItem[] = [ANGKOR, COKE, NOODLE, MAMA];

const DASHBOARD: DashboardResponse = {
  generated_at: '2026-09-14T00:00:00',
  summary: {
    items_needing_attention: 8,
    healthy_items: 4,
    total_inventory_value: 1180.05,
    // Real backend order: (priority, product_id) for actionable products.
    top_priorities: [
      ANGKOR,
      {
        product_id: 'mama-chicken',
        product_name: 'Mama Instant Noodles Chicken / មីសួសម៉ាម៉ា',
        category: 'Instant Noodles',
        current_stock: 8,
        status: 'REORDER',
        days_remaining: 0.3835616438356164,
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
        product_id: 'sardines-155g',
        product_name: 'Canned Sardines 155g / ត្រីកោប៉ង់',
        category: 'Canned Goods',
        current_stock: 90,
        status: 'REDUCE EXCESS',
        days_remaining: 74.11764705882354,
      },
      {
        product_id: 'eggs-10',
        product_name: 'Eggs (10 pcs) / ស៊ាងគោក្រហម',
        category: 'Fresh',
        current_stock: 25,
        status: 'MONITOR / PREPARE',
        days_remaining: 2.4647887323943665,
      },
    ],
  },
  ai_brief_context: {
    generated_at: '2026-09-14T00:00:00',
    currency: 'USD',
    total_inventory_value: 1180.05,
    items_needing_attention: 8,
    healthy_items: 4,
    top_priorities: [],
  },
};

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
      ['2026-09-01', 20],
      ['2026-09-07', 20],
      ['2026-09-14', 21],
    ],
    inventory_history: [
      ['2026-09-01', 6],
      ['2026-09-07', 8],
      ['2026-09-14', 8],
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
    currency: 'USD',
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
    ['2026-09-01', 6],
    ['2026-09-07', 8],
    ['2026-09-14', 8],
  ],
};

const ANALYTICS: AnalyticsResponse = {
  generated_at: '2026-09-14T00:00:00',
  products: [
    MAMA_DETAIL.analytics,
    {
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
        ['2026-09-14', 14],
      ],
      inventory_history: [
        ['2026-09-01', 106],
        ['2026-09-07', 140],
        ['2026-09-14', 180],
      ],
    },
  ],
  ai_insight_context: {
    generated_at: '2026-09-14T00:00:00',
    currency: 'USD',
    focus_area: 'demand',
    verified_trends: ['2 product(s) with stable demand'],
    product_highlights: [],
  },
};

const AI_BRIEF: AIExplanationResponse = {
  summary: 'TEST_APP_BRIEF Eight products need attention today.',
  reason: 'TEST_APP_BRIEF_REASON Two products could run out before their shipments.',
  action_explanation: 'TEST_APP_BRIEF_ACTION Review the top priorities first.',
  future_note: 'TEST_APP_BRIEF_NOTE Check the incoming shipments.',
  ai_available: true,
};

const AI_RECOMMENDATION: AIExplanationResponse = {
  summary: 'TEST_APP_RECOMMENDATION Reorder this product now.',
  reason: 'TEST_APP_RECOMMENDATION_REASON Stock is below the incoming shipment timing.',
  action_explanation: 'TEST_APP_RECOMMENDATION_ACTION Follow the recommendation above.',
  future_note: 'TEST_APP_RECOMMENDATION_NOTE Review after the delivery.',
  ai_available: true,
};

const AI_INSIGHT: AIExplanationResponse = {
  summary: 'TEST_APP_INSIGHT Demand is stable across your products.',
  reason: 'TEST_APP_INSIGHT_REASON Most products show steady demand.',
  action_explanation: 'TEST_APP_INSIGHT_ACTION Watch the low-stock products.',
  future_note: 'TEST_APP_INSIGHT_NOTE No forecasting is performed.',
  ai_available: true,
};

async function fulfillJson(route: Route, json: unknown) {
  await route.fulfill({
    headers: { 'Access-Control-Allow-Origin': '*' },
    json,
  });
}

test.beforeEach(async ({ page }) => {
  await page.route('**/api/v1/settings', (route) => fulfillJson(route, SETTINGS));
  await page.route('**/api/v1/dashboard', (route) => fulfillJson(route, DASHBOARD));
  await page.route('**/api/v1/inventory', (route) => fulfillJson(route, INVENTORY));
  await page.route('**/api/v1/inventory/mama-chicken', (route) =>
    fulfillJson(route, MAMA_DETAIL),
  );
  await page.route('**/api/v1/analytics', (route) => fulfillJson(route, ANALYTICS));
  await page.route('**/api/v1/ai/business-brief', (route) =>
    fulfillJson(route, AI_BRIEF),
  );
  await page.route('**/api/v1/ai/recommendation/*', (route) =>
    fulfillJson(route, AI_RECOMMENDATION),
  );
  await page.route('**/api/v1/ai/insight', (route) => fulfillJson(route, AI_INSIGHT));
});

test('the shell shows the configured business name and navigation moves through all pages', async ({
  page,
}) => {
  await page.goto('/dashboard');
  await expect(
    page.getByRole('heading', { name: 'Dashboard', level: 1 }),
  ).toBeVisible();

  // The configured business name is shown by the shared shell (sidebar).
  const sidebar = page.locator('aside');
  await expect(sidebar.getByText("Chen's Mini-Mart")).toBeVisible();
  await expect(
    sidebar.getByRole('link', { name: 'Dashboard' }),
  ).toHaveAttribute('aria-current', 'page');

  await sidebar.getByRole('link', { name: 'Inventory' }).click();
  await expect(page).toHaveURL(/\/inventory$/);
  await expect(
    page.getByRole('heading', { name: 'Inventory', level: 1 }),
  ).toBeVisible();
  await expect(
    sidebar.getByRole('link', { name: 'Inventory' }),
  ).toHaveAttribute('aria-current', 'page');

  // Open a product through the real list.
  await page.getByRole('link', { name: /Mama Instant Noodles Chicken/ }).click();
  await expect(
    page.getByRole('heading', {
      level: 1,
      name: /Mama Instant Noodles Chicken/,
    }),
  ).toBeVisible();
  await expect(page.getByText('Reorder 130 units')).toBeVisible();

  await sidebar.getByRole('link', { name: 'Analytics' }).click();
  await expect(page).toHaveURL(/\/analytics$/);
  await expect(
    page.getByRole('heading', { name: 'Analytics', level: 1 }),
  ).toBeVisible();

  await sidebar.getByRole('link', { name: 'Settings' }).click();
  await expect(page).toHaveURL(/\/settings$/);
  await expect(
    page.getByRole('heading', { name: 'Settings', level: 1 }),
  ).toBeVisible();

  await sidebar.getByRole('link', { name: 'Dashboard' }).click();
  await expect(
    page.getByRole('heading', { name: 'Dashboard', level: 1 }),
  ).toBeVisible();
});

test('one configured currency is used consistently on Dashboard, Analytics, Product Detail and Settings', async ({
  page,
}) => {
  await page.goto('/dashboard');
  await expect(page.getByText('$1,180.05')).toBeVisible();

  await page.goto('/inventory/mama-chicken');
  await expect(
    page.getByRole('heading', {
      level: 1,
      name: /Mama Instant Noodles Chicken/,
    }),
  ).toBeVisible();
  await expect(page.getByText('$2.80')).toBeVisible();

  await page.goto('/analytics');
  const financial = page.getByRole('region', { name: 'Financial analytics' });
  const mamaFinancial = financial.getByRole('row', {
    name: /Mama Instant Noodles Chicken/,
  });
  await expect(mamaFinancial).toContainText('$175.20');
  await expect(mamaFinancial).toContainText('$102.20');
  await expect(mamaFinancial).toContainText('$73.00');

  const inventory = page.getByRole('region', { name: 'Inventory analytics' });
  await expect(
    inventory.getByRole('row', { name: /Mama Instant Noodles Chicken/ }),
  ).toContainText('$2.80');

  await page.goto('/settings');
  const profile = page.getByRole('region', { name: 'Business profile' });
  await expect(profile).toContainText('USD');
});

test('without a configured currency money is shown plain and Settings says so', async ({
  page,
}) => {
  await page.route('**/api/v1/settings', (route) =>
    fulfillJson(route, { ...SETTINGS, currency: null }),
  );

  await page.goto('/dashboard');
  await expect(page.getByText('1,180.05')).toBeVisible();
  await expect(page.getByRole('main')).not.toContainText('$');

  await page.goto('/settings');
  const profile = page.getByRole('region', { name: 'Business profile' });
  await expect(profile).toContainText('money values are shown without a currency');
});

test('the shell falls back to a neutral label when no business name is configured', async ({
  page,
}) => {
  await page.route('**/api/v1/settings', (route) =>
    fulfillJson(route, { ...SETTINGS, business_name: null }),
  );

  await page.goto('/dashboard');
  await expect(page.locator('aside').getByText('Your business')).toBeVisible();
  await expect(page.locator('aside').getByText("Chen's Mini-Mart")).toHaveCount(0);
});

test('no backend secret reaches the browser', async ({ page }) => {
  const requests: string[] = [];
  page.on('request', (request) => requests.push(request.url()));

  for (const path of [
    '/dashboard',
    '/inventory',
    '/inventory/mama-chicken',
    '/analytics',
    '/settings',
  ]) {
    await page.goto(path);
  }

  // Only the app itself and the InventoryIQ API are contacted.
  for (const url of requests) {
    expect(url).not.toMatch(/googleapis|private_key|client_email/);
    expect(url).not.toMatch(/key=[A-Za-z0-9_-]{10,}/);
  }

  const main = page.getByRole('main');
  for (const secret of [
    'GEMINI_API_KEY',
    'GOOGLE_SHEET_ID',
    'GOOGLE_SERVICE_ACCOUNT_FILE',
    'private_key',
    'BEGIN PRIVATE KEY',
  ]) {
    await expect(main).not.toContainText(secret);
  }
});

test('every page has no horizontal overflow on mobile and mobile navigation works', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });

  const pages: Array<[string, string]> = [
    ['/dashboard', 'Dashboard'],
    ['/inventory', 'Inventory'],
    ['/inventory/mama-chicken', 'Mama Instant Noodles Chicken'],
    ['/analytics', 'Analytics'],
    ['/settings', 'Settings'],
  ];

  for (const [path, heading] of pages) {
    await page.goto(path);
    await expect(
      page.getByRole('heading', { level: 1, name: heading }),
    ).toBeVisible();
    const overflow = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(overflow.scrollWidth, `overflow on ${path}`).toBeLessThanOrEqual(
      overflow.clientWidth,
    );
  }

  // The compact mobile navigation is usable and moves between pages.
  const mobileNav = page.locator('header nav');
  await mobileNav.getByRole('link', { name: 'Inventory' }).click();
  await expect(page).toHaveURL(/\/inventory$/);
  await expect(
    page.getByRole('heading', { name: 'Inventory', level: 1 }),
  ).toBeVisible();
});
