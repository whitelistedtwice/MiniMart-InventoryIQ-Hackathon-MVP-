/*
  Display-only formatting for the Dashboard.

  These helpers format backend-provided values. They never calculate
  business metrics, and they never turn missing data (null) into 0.
*/

const MISSING = "—";

export function formatCount(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

/** Money value from the backend. null = unavailable, shown as "—". */
export function formatMoney(value: number | null | undefined): string {
  if (value == null) return MISSING;
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/** Days of stock remaining. null = unavailable, shown as "—". */
export function formatDays(value: number | null | undefined): string {
  if (value == null) return MISSING;
  const rounded = Math.round(value * 10) / 10;
  const label = Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
  return `${label} ${rounded === 1 ? "day" : "days"}`;
}

/** Current stock. null = unavailable, shown as "—". 0 stays 0. */
export function formatStock(value: number | null | undefined): string {
  if (value == null) return MISSING;
  return formatCount(value);
}
