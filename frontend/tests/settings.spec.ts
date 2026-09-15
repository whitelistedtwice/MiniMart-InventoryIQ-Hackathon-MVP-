import { expect, test, type Route } from '@playwright/test';

import type { SettingsResponse } from '../app/types';

/*
  Settings page tests (Phase 14).

  Fixtures follow the ACTUAL `/api/v1/settings` contract:
  SettingsResponse { business_name?, business_type?, sheets_connected, last_sync_at? }.
  The backend currently reports `sheets_connected` as configuration presence only
  (not a live connectivity probe), so the UI uses honest "Configured" /
  "Not configured" labels rather than "Connected".

  The page is read-only: there is no Save, no Connect/Reconnect, and no
  credentials or secrets displayed.
*/

const SETTINGS_CONFIGURED: SettingsResponse = {
  business_name: "Chen's Mini-Mart",
  business_type: 'Mini-mart',
  sheets_connected: true,
  last_sync_at: '2026-09-14T08:30:00',
};

const SETTINGS_UNCONFIGURED: SettingsResponse = {
  business_name: null,
  business_type: null,
  sheets_connected: false,
  last_sync_at: null,
};

async function fulfillJson(route: Route, json: unknown) {
  await route.fulfill({
    headers: { 'Access-Control-Allow-Origin': '*' },
    json,
  });
}

async function fulfillSettings(route: Route) {
  await fulfillJson(route, SETTINGS_CONFIGURED);
}

test.beforeEach(async ({ page }) => {
  await page.route('**/api/v1/settings', fulfillSettings);
});

test('settings renders the real backend contract and business profile', async ({
  page,
}) => {
  await page.goto('/settings');
  await expect(
    page.getByRole('heading', { name: 'Settings', level: 1 }),
  ).toBeVisible();

  const profile = page.getByRole('region', { name: 'Business profile' });
  await expect(profile).toContainText("Chen's Mini-Mart");
  await expect(profile).toContainText('Mini-mart');

  const connection = page.getByRole('region', { name: 'Google Sheets connection' });
  await expect(connection).toContainText('Configured');
  await expect(connection).toContainText('Google Sheets credentials are configured.');
  await expect(connection).toContainText(/14 Sep(t)? 2026/);
});

test('connection state uses the backend semantics: configured, not "live connected"', async ({
  page,
}) => {
  await page.goto('/settings');
  const connection = page.getByRole('region', { name: 'Google Sheets connection' });

  // Honest wording for a configuration-presence boolean.
  await expect(connection.getByText('Configured', { exact: true })).toBeVisible();
  await expect(connection).not.toContainText('Connected and working');
  await expect(connection).not.toContainText('Live connection verified');
  await expect(connection).not.toContainText('Syncing successfully');
});

test('missing optional values are handled safely without fabricated data', async ({
  page,
}) => {
  await page.route('**/api/v1/settings', (route) =>
    fulfillJson(route, SETTINGS_UNCONFIGURED),
  );
  await page.goto('/settings');

  const profile = page.getByRole('region', { name: 'Business profile' });
  await expect(profile).toContainText('—');
  await expect(profile).not.toContainText('Coffee Corner');
  await expect(profile).not.toContainText('Mini-mart');

  const connection = page.getByRole('region', { name: 'Google Sheets connection' });
  await expect(connection.getByText('Not configured', { exact: true })).toBeVisible();
  await expect(connection).toContainText(
    'Google Sheets credentials are not configured yet.',
  );
});

test('shows a friendly error state and recovers on retry', async ({ page }) => {
  let settingsRequests = 0;
  let shouldFail = true;
  await page.route('**/api/v1/settings', async (route) => {
    settingsRequests += 1;
    if (!shouldFail) {
      await fulfillSettings(route);
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

  await page.goto('/settings');

  const errorHeading = page.getByRole('heading', {
    name: "We couldn't load your settings",
  });
  await expect(errorHeading).toBeVisible();
  await expect(
    page.getByRole('status', { name: 'Loading settings' }),
  ).toHaveCount(0);

  const main = page.getByRole('main');
  await expect(main).not.toContainText('data_access_error');
  await expect(main).not.toContainText('simulated backend failure');

  const requestsAtError = settingsRequests;
  shouldFail = false;
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.getByRole('region', { name: 'Business profile' })).toBeVisible();
  await expect(errorHeading).toHaveCount(0);
  expect(settingsRequests).toBe(requestsAtError + 1);
});

test('loading state is shown while the settings request is pending', async ({
  page,
}) => {
  let releaseSettings!: () => void;
  const settingsHeld = new Promise<void>((resolve) => {
    releaseSettings = resolve;
  });

  await page.route('**/api/v1/settings', async (route) => {
    await settingsHeld;
    await fulfillSettings(route);
  });

  const settingsRequest = page.waitForRequest('**/api/v1/settings');
  await page.goto('/settings');
  await settingsRequest;

  const loading = page.getByRole('status', { name: 'Loading settings' });
  await expect(loading).toBeVisible();
  await expect(page.getByRole('region', { name: 'Business profile' })).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: "We couldn't load your settings" }),
  ).toHaveCount(0);

  releaseSettings();
  await expect(page.getByRole('region', { name: 'Business profile' })).toBeVisible();
  await expect(loading).toHaveCount(0);
});

test('no secrets or unsupported interactions are rendered', async ({ page }) => {
  await page.goto('/settings');
  const main = page.getByRole('main');

  // Security: no credentials or secrets appear.
  await expect(main).not.toContainText('GOOGLE_SHEET_ID');
  await expect(main).not.toContainText('GOOGLE_SERVICE_ACCOUNT_FILE');
  await expect(main).not.toContainText('service-account');
  await expect(main).not.toContainText('private key');
  await expect(main).not.toContainText('GEMINI_API_KEY');
  await expect(main).not.toContainText('access token');

  // Scope: no fake interactive controls.
  await expect(page.getByRole('button', { name: 'Save' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Connect' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Reconnect' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Sync now' })).toHaveCount(0);
  await expect(page.getByLabel('Password')).toHaveCount(0);
  await expect(page.getByLabel('Email')).toHaveCount(0);
  await expect(main).not.toContainText('Notifications');
  await expect(main).not.toContainText('Billing');
  await expect(main).not.toContainText('Danger Zone');
  await expect(main).not.toContainText('Team');
});

test('settings has no page overflow on mobile and no console errors', async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/settings');
  await expect(page.getByRole('heading', { name: 'Settings', level: 1 })).toBeVisible();

  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth);

  // Refresh remains usable on mobile.
  await expect(page.getByRole('button', { name: 'Refresh' })).toBeVisible();

  expect(consoleErrors).toEqual([]);
});
