import type { DemandTrend } from "@/app/types";

/*
  Display-only formatting shared across pages.

  These helpers format backend-provided values. They never calculate
  business metrics, and they never turn missing data (null) into 0.
*/

const MISSING = "—";

export function formatCount(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

/**
 * Money value from the backend. null = unavailable, shown as "—".
 *
 * The business currency comes from backend configuration. When it is
 * configured (ISO 4217 code) every money value is shown in that one
 * currency; when it is missing — or the code is not recognized — the
 * amount is shown plain, never with an invented currency.
 */
export function formatMoney(
  value: number | null | undefined,
  currency?: string | null,
): string {
  if (value == null) return MISSING;
  if (currency) {
    try {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(value);
    } catch {
      // Unknown currency code — fall back to the plain amount below.
    }
  }
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

/** Decimal value with a bounded number of digits. null = "—". */
export function formatDecimal(
  value: number | null | undefined,
  digits = 1,
): string {
  if (value == null) return MISSING;
  const factor = 10 ** digits;
  const rounded = Math.round(value * factor) / factor;
  return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(digits);
}

/** Current stock. null = unavailable, shown as "—". 0 stays 0. */
export function formatStock(value: number | null | undefined): string {
  if (value == null) return MISSING;
  return formatCount(value);
}

/**
 * ISO date (YYYY-MM-DD) or datetime (YYYY-MM-DDTHH:mm:ss) from the backend,
 * formatted for display. Only the calendar portion is used so the timezone
 * never shifts the day.
 */
export function formatDate(value: string | null | undefined): string {
  if (!value) return MISSING;
  const datePart = value.split(/[T ]/)[0];
  const [year, month, day] = datePart.split("-").map(Number);
  if (!year || !month || !day) return value;
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(year, month - 1, day));
}

const TREND_LABELS: Record<DemandTrend, string> = {
  increasing: "Increasing",
  stable: "Stable",
  decreasing: "Decreasing",
  unavailable: "Unavailable",
};

/** Backend demand trend enum, labelled for display. */
export function formatTrend(value: DemandTrend | null | undefined): string {
  if (!value) return MISSING;
  return TREND_LABELS[value] ?? MISSING;
}
