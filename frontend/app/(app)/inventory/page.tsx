"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import type { ProductListItem, RecommendationAction } from "@/app/types";
import { ProductTable } from "@/components/inventory/ProductTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState, Skeleton } from "@/components/ui/LoadingState";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";
import { useApiGet } from "@/lib/api/hooks";
import { API_ROUTES } from "@/lib/api/routes";

/*
  Inventory list (Phase 12).

  The single authoritative product search lives here. Filtering is pure
  client-side presentation over the backend product list — no business
  metrics are recomputed.
*/

const STATUS_OPTIONS: RecommendationAction[] = [
  "REORDER",
  "REDUCE EXCESS",
  "MONITOR / PREPARE",
  "NO ACTION",
  "UNAVAILABLE",
];

function InventorySkeleton() {
  return (
    <LoadingState label="Loading inventory">
      <div className="space-y-4">
        <div className="flex flex-wrap gap-3">
          <Skeleton className="h-10 w-full max-w-sm" />
          <Skeleton className="h-10 w-40" />
          <Skeleton className="h-10 w-40" />
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    </LoadingState>
  );
}

function InventoryContent() {
  const inventory = useApiGet<ProductListItem[]>(API_ROUTES.inventory);

  // The global top-bar search navigates to /inventory?q=…; this page owns
  // the only search state and simply adopts that query.
  const searchParams = useSearchParams();
  const urlQuery = searchParams.get("q") ?? "";
  const [query, setQuery] = useState(urlQuery);
  const [category, setCategory] = useState("all");
  const [status, setStatus] = useState<"all" | RecommendationAction>("all");

  useEffect(() => {
    setQuery(urlQuery);
  }, [urlQuery]);

  const products = inventory.data ?? [];

  const categories = useMemo(() => {
    const unique = new Set(
      products
        .map((product) => product.category)
        .filter((value): value is string => !!value),
    );
    return Array.from(unique).sort((a, b) => a.localeCompare(b));
  }, [products]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return products.filter((product) => {
      if (category !== "all" && product.category !== category) return false;
      if (status !== "all" && product.status !== status) return false;
      if (needle && !product.product_name.toLowerCase().includes(needle)) {
        return false;
      }
      return true;
    });
  }, [products, query, category, status]);

  if (inventory.loading) return <InventorySkeleton />;

  if (inventory.error) {
    return (
      <ErrorState
        title="We couldn't load your inventory"
        description={
          inventory.error.kind === "network"
            ? "The InventoryIQ server didn't respond. Check that it is running, then try again."
            : "The server couldn't load your inventory right now. Please try again."
        }
        onRetry={inventory.reload}
      />
    );
  }

  if (products.length === 0) {
    return (
      <EmptyState
        icon="inbox"
        title="No products yet"
        description="Once your products are available from the connected Google Sheet, they will appear here."
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-sm">
          <label htmlFor="inventory-search" className="sr-only">
            Search products
          </label>
          <input
            id="inventory-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search products…"
            className="h-10 w-full rounded-lg border border-line bg-surface px-3 text-sm text-ink placeholder:text-muted focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
          />
        </div>

        <div>
          <label htmlFor="inventory-category" className="sr-only">
            Filter by category
          </label>
          <select
            id="inventory-category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="h-10 rounded-lg border border-line bg-surface px-3 text-sm text-ink focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
          >
            <option value="all">All Categories</option>
            {categories.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="inventory-status" className="sr-only">
            Filter by status
          </label>
          <select
            id="inventory-status"
            value={status}
            onChange={(event) =>
              setStatus(event.target.value as "all" | RecommendationAction)
            }
            className="h-10 rounded-lg border border-line bg-surface px-3 text-sm text-ink focus:border-brand focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
          >
            <option value="all">All Statuses</option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <p className="ml-auto text-sm text-muted">
          Showing {filtered.length} of {products.length} products
        </p>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon="search"
          title="No products found"
          description="No products match your search or filters. Try a different term or clear the filters."
        />
      ) : (
        <ProductTable products={filtered} />
      )}
    </div>
  );
}

export default function InventoryPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Inventory"
        description="Manage your products and stock levels."
      />
      <Suspense fallback={<InventorySkeleton />}>
        <InventoryContent />
      </Suspense>
    </PageContainer>
  );
}
