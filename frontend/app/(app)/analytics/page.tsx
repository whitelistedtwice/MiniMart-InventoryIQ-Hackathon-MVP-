"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import type { AnalyticsResponse, ProductAnalytics } from "@/app/types";
import { AnalyticsAiInsight } from "@/components/analytics/AnalyticsAiInsight";
import { SalesTrendChart } from "@/components/analytics/SalesTrendChart";
import { StockTrendChart } from "@/components/inventory/StockTrendChart";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Icon } from "@/components/ui/icons";
import { LoadingState, Skeleton } from "@/components/ui/LoadingState";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";
import { useApiGet } from "@/lib/api/hooks";
import { API_ROUTES } from "@/lib/api/routes";
import {
  formatDays,
  formatDecimal,
  formatMoney,
  formatStock,
  formatTrend,
} from "@/lib/format";

/*
  Analytics (Phase 13).

  A presentation layer over the deterministic `/api/v1/analytics` contract:
  per-product demand, inventory, and financial analytics plus raw history
  series for simple observed-trend charts. Every number, status, and trend
  comes from the backend — this page never calculates business metrics and
  never turns missing data into zero. AI insight is loaded lazily and
  separately so Gemini can never block or break the deterministic content.
*/

function ProductCell({ product }: { product: ProductAnalytics }) {
  return (
    <Link
      href={`/inventory/${encodeURIComponent(product.product_id)}`}
      className="font-medium text-ink hover:text-brand-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
    >
      {product.product_name}
    </Link>
  );
}

function SectionTable({
  ariaLabel,
  title,
  explainer,
  minWidth,
  headers,
  children,
}: {
  ariaLabel: string;
  title: string;
  explainer: string;
  minWidth: string;
  headers: string[];
  children: React.ReactNode;
}) {
  return (
    <section aria-label={ariaLabel} className="space-y-3">
      <div>
        <h2 className="text-lg font-semibold text-ink">{title}</h2>
        <p className="mt-0.5 text-sm text-muted">{explainer}</p>
      </div>
      <Card padded={false} className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className={`w-full text-left text-sm ${minWidth}`}>
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                {headers.map((header) => (
                  <th key={header} scope="col" className="px-5 py-3 font-medium">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-line">{children}</tbody>
          </table>
        </div>
      </Card>
    </section>
  );
}

const CONDITION_LABELS: Record<string, { label: string; className: string }> = {
  low: { label: "Low", className: "text-danger" },
  healthy: { label: "Healthy", className: "text-success" },
  excess: { label: "Excess", className: "text-excess" },
};

function ConditionValue({ status }: { status: string | null | undefined }) {
  if (!status) return <span className="text-ink-soft">—</span>;
  const condition = CONDITION_LABELS[status] ?? null;
  if (!condition) return <span className="text-ink-soft">—</span>;
  return (
    <span className={`font-medium ${condition.className}`}>
      {condition.label}
    </span>
  );
}

/** Highest-selling first (backend value); products without sales data last. */
function sortBySold(products: ProductAnalytics[]): ProductAnalytics[] {
  return [...products].sort(
    (a, b) => (b.demand.total_sold ?? -1) - (a.demand.total_sold ?? -1),
  );
}

/** Stable name order for inventory/financial tables, like the Inventory list. */
function sortByName(products: ProductAnalytics[]): ProductAnalytics[] {
  return [...products].sort((a, b) =>
    a.product_name.localeCompare(b.product_name),
  );
}

function AnalyticsSkeleton() {
  return (
    <LoadingState label="Loading analytics">
      <div className="space-y-6">
        <div className="space-y-3">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-64 w-full" />
        </div>
        <div className="space-y-3">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-64 w-full" />
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    </LoadingState>
  );
}

function MarginValue({ value }: { value: number | null | undefined }) {
  if (value == null) return <span className="text-ink-soft">—</span>;
  return <span className="tabular-nums">{formatDecimal(value * 100)}%</span>;
}

export default function AnalyticsPage() {
  const analytics = useApiGet<AnalyticsResponse>(API_ROUTES.analytics);
  const products = analytics.data?.products ?? [];

  const demandProducts = useMemo(
    () => (analytics.data ? sortBySold(analytics.data.products) : []),
    [analytics.data],
  );
  const namedProducts = useMemo(
    () => (analytics.data ? sortByName(analytics.data.products) : []),
    [analytics.data],
  );

  // Historical trends: one product at a time, defaulting to the first
  // product that has observable sales history.
  const defaultProductId = useMemo(
    () =>
      namedProducts.find((product) => product.sales_history.length >= 2)
        ?.product_id ?? namedProducts[0]?.product_id ?? null,
    [namedProducts],
  );
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selectedProductId = selectedId ?? defaultProductId;
  const selectedProduct = namedProducts.find(
    (product) => product.product_id === selectedProductId,
  );

  if (analytics.loading) {
    return (
      <PageContainer>
        <PageHeader
          title="Analytics"
          description="Understand your sales, inventory and trends. Make better decisions with your data."
        />
        <AnalyticsSkeleton />
      </PageContainer>
    );
  }

  if (analytics.error) {
    return (
      <PageContainer>
        <PageHeader
          title="Analytics"
          description="Understand your sales, inventory and trends. Make better decisions with your data."
        />
        <ErrorState
          title="We couldn't load your analytics"
          description={
            analytics.error.kind === "network"
              ? "The InventoryIQ server didn't respond. Check that it is running, then try again."
              : "The server couldn't load your analytics right now. Please try again."
          }
          onRetry={analytics.reload}
        />
      </PageContainer>
    );
  }

  if (!analytics.data || analytics.data.products.length === 0) {
    return (
      <PageContainer>
        <PageHeader
          title="Analytics"
          description="Understand your sales, inventory and trends. Make better decisions with your data."
        />
        <EmptyState
          icon="inbox"
          title="No analytics available yet"
          description="Once your products are available from the connected Google Sheet, your demand, inventory, and financial analytics will appear here."
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Analytics"
        description="Understand your sales, inventory and trends. Make better decisions with your data."
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={analytics.reload}
            disabled={analytics.loading}
          >
            <Icon name="refresh" width={16} height={16} />
            Refresh
          </Button>
        }
      />

      <div className="space-y-8">
        <SectionTable
          ariaLabel="Demand analytics"
          title="Demand"
          explainer="How much each product is selling, with the recent demand next to the overall average."
          minWidth="min-w-[640px]"
          headers={["Product", "Total Sold", "Avg / Day", "Recent / Day", "Trend"]}
        >
          {demandProducts.map((product) => (
            <tr
              key={product.product_id}
              className="transition-colors hover:bg-canvas"
            >
              <td className="px-5 py-3.5">
                <ProductCell product={product} />
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatStock(product.demand.total_sold)}
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatDecimal(product.demand.average_daily_sales)}
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatDecimal(product.demand.recent_daily_sales)}
              </td>
              <td className="px-5 py-3.5 text-ink-soft">
                {formatTrend(product.demand.trend)}
              </td>
            </tr>
          ))}
        </SectionTable>

        <SectionTable
          ariaLabel="Inventory analytics"
          title="Inventory"
          explainer="Current stock, how long it lasts, and what it is worth. Incoming shipments are listed separately."
          minWidth="min-w-[780px]"
          headers={[
            "Product",
            "Current Stock",
            "Days Left",
            "Inventory Value",
            "Incoming",
            "Condition",
          ]}
        >
          {namedProducts.map((product) => (
            <tr
              key={product.product_id}
              className="transition-colors hover:bg-canvas"
            >
              <td className="px-5 py-3.5">
                <ProductCell product={product} />
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatStock(product.inventory.current_stock)}
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatDays(product.inventory.days_of_stock_remaining)}
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatMoney(product.inventory.inventory_value)}
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatStock(product.shipment.incoming_quantity)}
              </td>
              <td className="px-5 py-3.5">
                <ConditionValue status={product.inventory.stock_status} />
              </td>
            </tr>
          ))}
        </SectionTable>

        <SectionTable
          ariaLabel="Financial analytics"
          title="Financial"
          explainer="Revenue, estimated cost, and estimated gross profit per product. Missing values are shown as unavailable."
          minWidth="min-w-[820px]"
          headers={[
            "Product",
            "Revenue",
            "Estimated Cost",
            "Estimated Profit",
            "Margin",
            "Financial Exposure",
          ]}
        >
          {namedProducts.map((product) => (
            <tr
              key={product.product_id}
              className="transition-colors hover:bg-canvas"
            >
              <td className="px-5 py-3.5">
                <ProductCell product={product} />
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatMoney(product.financial.revenue)}
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatMoney(product.financial.estimated_cost)}
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatMoney(product.financial.profit)}
              </td>
              <td className="px-5 py-3.5">
                <MarginValue value={product.financial.profit_margin} />
              </td>
              <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                {formatMoney(product.financial.financial_exposure)}
              </td>
            </tr>
          ))}
        </SectionTable>

        <section aria-label="Historical trends" className="space-y-3">
          <div>
            <h2 className="text-lg font-semibold text-ink">Historical Trends</h2>
            <p className="mt-0.5 text-sm text-muted">
              Observed sales and stock levels over time for one product. These
              are past observations, not forecasts.
            </p>
          </div>
          <div>
            <label htmlFor="analytics-product" className="sr-only">
              Choose product
            </label>
            <select
              id="analytics-product"
              value={selectedProductId ?? ""}
              onChange={(event) => setSelectedId(event.target.value)}
              className="h-10 rounded-lg border border-line bg-surface px-3 text-sm text-ink focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
            >
              {namedProducts.map((product) => (
                <option key={product.product_id} value={product.product_id}>
                  {product.product_name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <h3 className="text-base font-semibold text-ink">
                Units Sold Per Day
              </h3>
              <div className="mt-3">
                {selectedProduct ? (
                  <SalesTrendChart points={selectedProduct.sales_history} />
                ) : null}
              </div>
            </Card>
            <Card>
              <h3 className="text-base font-semibold text-ink">
                Stock Level Over Time
              </h3>
              <div className="mt-3">
                {selectedProduct ? (
                  <StockTrendChart points={selectedProduct.inventory_history} />
                ) : null}
              </div>
            </Card>
          </div>
        </section>

        <AnalyticsAiInsight />
      </div>
    </PageContainer>
  );
}
