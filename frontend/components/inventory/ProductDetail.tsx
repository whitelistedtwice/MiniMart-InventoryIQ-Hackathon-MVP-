"use client";

import Link from "next/link";

import type { ProductDetailResponse, RecommendationResult } from "@/app/types";
import { ProductAiInsight } from "@/components/inventory/ProductAiInsight";
import { StockTrendChart } from "@/components/inventory/StockTrendChart";
import { useCurrency } from "@/components/layout/SettingsProvider";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Icon, type IconName } from "@/components/ui/icons";
import { LoadingState, Skeleton } from "@/components/ui/LoadingState";
import { PageContainer } from "@/components/ui/PageContainer";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useApiGet } from "@/lib/api/hooks";
import { API_ROUTES } from "@/lib/api/routes";
import {
  formatDate,
  formatDays,
  formatDecimal,
  formatMoney,
  formatStock,
  formatTrend,
} from "@/lib/format";

/*
  Product Detail (Phase 12).

  Read/analysis only: no stock adjustment, no editing, no write-back.
  Current stock and incoming shipments are always presented separately.
  Every number and status is backend-provided; nothing is recomputed here.
*/

function StatCard({
  icon,
  tone,
  label,
  value,
  hint,
}: {
  icon: IconName;
  tone: string;
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <Card className="flex items-start gap-4">
      <span
        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${tone}`}
        aria-hidden="true"
      >
        <Icon name={icon} />
      </span>
      <div className="min-w-0">
        <p className="text-xs font-medium uppercase tracking-wide text-muted">
          {label}
        </p>
        <p className="mt-0.5 text-2xl font-semibold tabular-nums text-ink">
          {value}
        </p>
        <p className="mt-0.5 text-xs text-muted">{hint}</p>
      </div>
    </Card>
  );
}

function recommendationHeadline(
  recommendation: RecommendationResult,
  excessUnits: number | null | undefined,
): string {
  switch (recommendation.action) {
    case "REORDER":
      return recommendation.reorder_quantity != null
        ? `Reorder ${formatStock(recommendation.reorder_quantity)} units`
        : "Reorder needed";
    case "REDUCE EXCESS":
      return excessUnits != null
        ? `Reduce about ${formatStock(excessUnits)} units`
        : "Reduce excess stock";
    case "MONITOR / PREPARE":
      return "Monitor and prepare";
    case "NO ACTION":
      return "No action needed";
    default:
      return "Not enough data for a recommendation";
  }
}

function sufficiencyNote(value: boolean | null | undefined): string | null {
  if (value === true) {
    return "The incoming shipment is expected to arrive before stock runs out.";
  }
  if (value === false) {
    return "Current stock may run out before the incoming shipment arrives.";
  }
  return null;
}

function DetailSkeleton() {
  return (
    <LoadingState label="Loading product">
      <div className="space-y-6">
        <Skeleton className="h-28 w-full" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Skeleton className="h-40 w-full" />
        <div className="grid gap-6 lg:grid-cols-3">
          <Skeleton className="h-72 w-full lg:col-span-2" />
          <Skeleton className="h-72 w-full" />
        </div>
      </div>
    </LoadingState>
  );
}

export function ProductDetail({ productId }: { productId: string }) {
  const detail = useApiGet<ProductDetailResponse>(API_ROUTES.product(productId));
  const currency = useCurrency();
  const backLink = (
    <Link
      href="/inventory"
      className="inline-flex items-center gap-1.5 text-sm font-medium text-brand hover:text-brand-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
    >
      <Icon name="arrow-left" width={16} height={16} />
      Back to Inventory
    </Link>
  );

  if (detail.loading) {
    return (
      <PageContainer>
        <div className="mb-4">{backLink}</div>
        <DetailSkeleton />
      </PageContainer>
    );
  }

  if (detail.error?.status === 404) {
    return (
      <PageContainer>
        <div className="mb-4">{backLink}</div>
        <EmptyState
          icon="search"
          title="Product not found"
          description="This product is not in the current inventory data. It may have been removed from the Google Sheet."
        />
      </PageContainer>
    );
  }

  if (detail.error || !detail.data) {
    return (
      <PageContainer>
        <div className="mb-4">{backLink}</div>
        <ErrorState
          title="We couldn't load this product"
          description={
            detail.error?.kind === "network"
              ? "The InventoryIQ server didn't respond. Check that it is running, then try again."
              : "The server couldn't load this product right now. Please try again."
          }
          onRetry={detail.reload}
        />
      </PageContainer>
    );
  }

  const { analytics, recommendation } = detail.data;
  const { demand, inventory, shipment } = analytics;
  const category = detail.data.ai_context.product.category ?? null;
  const note = sufficiencyNote(recommendation.incoming_stock_sufficient);
  const incomingCount = shipment.incoming_quantity ?? 0;

  return (
    <PageContainer>
      <div className="mb-4">{backLink}</div>

      <div className="space-y-6">
        <Card>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <h1 className="break-words text-2xl font-semibold tracking-tight text-ink">
                {analytics.product_name}
              </h1>
              <p className="mt-1 text-sm text-muted">{category ?? "—"}</p>
            </div>
            <div className="flex items-center gap-3">
              <StatusBadge status={recommendation.action} />
              <span className="text-sm font-medium text-ink-soft">
                {formatDays(inventory.days_of_stock_remaining)} left
              </span>
            </div>
          </div>
        </Card>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon="inventory"
            tone="bg-brand-soft text-brand"
            label="Current Stock"
            value={formatStock(inventory.current_stock)}
            hint="Physical stock on hand"
          />
          <StatCard
            icon="calendar"
            tone="bg-danger-soft text-danger"
            label="Days Left"
            value={formatDays(inventory.days_of_stock_remaining)}
            hint="At the current demand"
          />
          <StatCard
            icon="analytics"
            tone="bg-success-soft text-success"
            label="Average Daily Demand"
            value={
              demand.average_daily_sales != null
                ? `${formatDecimal(demand.average_daily_sales)} / day`
                : "—"
            }
            hint={`Trend: ${formatTrend(demand.trend)}`}
          />
          <StatCard
            icon="truck"
            tone="bg-brand-soft text-brand"
            label="Incoming Shipments"
            value={formatStock(shipment.incoming_quantity)}
            hint={
              incomingCount > 0
                ? `Arrives ${formatDate(shipment.expected_arrival)}`
                : "No incoming shipment"
            }
          />
        </div>

        <Card className="border-l-4 border-l-brand">
          <div className="flex items-start gap-3">
            <span
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-soft text-brand"
              aria-hidden="true"
            >
              <Icon name="check" width={18} height={18} />
            </span>
            <div className="min-w-0">
              <h2 className="text-base font-semibold text-ink">
                Recommendation
              </h2>
              <p className="mt-1 text-lg font-semibold text-ink">
                {recommendationHeadline(
                  recommendation,
                  inventory.excess_units,
                )}
              </p>
              {recommendation.reorder_timing ? (
                <p className="mt-0.5 text-sm text-ink-soft">
                  {recommendation.reorder_timing}
                </p>
              ) : note ? (
                <p className="mt-0.5 text-sm text-ink-soft">{note}</p>
              ) : null}

              {recommendation.evidence.length > 0 ? (
                <ul className="mt-3 space-y-1.5">
                  {recommendation.evidence.map((reason, index) => (
                    <li
                      key={`${index}-${reason}`}
                      className="flex gap-2 text-sm text-ink-soft"
                    >
                      <span aria-hidden="true" className="text-muted">
                        •
                      </span>
                      {reason}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-3 text-sm text-muted">
                  No evidence was provided for this recommendation.
                </p>
              )}
            </div>
          </div>
        </Card>

        <div className="grid items-start gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <h2 className="text-base font-semibold text-ink">Stock Trend</h2>
            <div className="mt-3">
              <StockTrendChart points={detail.data.historical_inventory} />
            </div>
          </Card>

          <div className="space-y-6">
            <Card>
              <h2 className="text-base font-semibold text-ink">
                Incoming Shipment
              </h2>
              {incomingCount > 0 ? (
                <dl className="mt-3 space-y-2 text-sm">
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Quantity</dt>
                    <dd className="tabular-nums font-medium text-ink">
                      {formatStock(shipment.incoming_quantity)} units
                    </dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Expected arrival</dt>
                    <dd className="font-medium text-ink">
                      {formatDate(shipment.expected_arrival)}
                    </dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-muted">Days until arrival</dt>
                    <dd className="tabular-nums font-medium text-ink">
                      {formatDays(shipment.days_until_arrival)}
                    </dd>
                  </div>
                </dl>
              ) : (
                <p className="mt-3 text-sm text-muted">
                  No incoming shipment for this product.
                </p>
              )}
              {note ? (
                <p className="mt-3 text-sm text-ink-soft">{note}</p>
              ) : null}
              <p className="mt-3 border-t border-line pt-3 text-xs text-muted">
                Incoming stock is not part of current stock.
              </p>
            </Card>

            <Card>
              <h2 className="text-base font-semibold text-ink">
                Product Details
              </h2>
              <dl className="mt-3 space-y-2 text-sm">
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Category</dt>
                  <dd className="text-right font-medium text-ink">
                    {category ?? "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Demand trend</dt>
                  <dd className="font-medium text-ink">
                    {formatTrend(demand.trend)}
                  </dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Inventory value</dt>
                  <dd className="tabular-nums font-medium text-ink">
                    {formatMoney(inventory.inventory_value, currency)}
                  </dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Target stock days</dt>
                  <dd className="tabular-nums font-medium text-ink">
                    {recommendation.target_stock_days != null
                      ? `${formatStock(recommendation.target_stock_days)} days`
                      : "—"}
                  </dd>
                </div>
              </dl>
            </Card>
          </div>
        </div>

        <ProductAiInsight productId={productId} />
      </div>
    </PageContainer>
  );
}
