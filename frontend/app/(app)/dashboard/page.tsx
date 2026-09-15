"use client";

import Link from "next/link";

import type { AIExplanationResponse, DashboardResponse } from "@/app/types";
import { AiBusinessBrief } from "@/components/dashboard/AiBusinessBrief";
import { BusinessHealth } from "@/components/dashboard/BusinessHealth";
import { TopPriorities } from "@/components/dashboard/TopPriorities";
import { useCurrency } from "@/components/layout/SettingsProvider";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Icon } from "@/components/ui/icons";
import { LoadingState, Skeleton } from "@/components/ui/LoadingState";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";
import { useApiGet } from "@/lib/api/hooks";
import { API_ROUTES } from "@/lib/api/routes";

/*
  Dashboard (Phase 11).

  Consumes the deterministic `/api/v1/dashboard` contract and the optional,
  separately-loaded `/api/v1/ai/business-brief`. Every number, status, and
  ordering comes from the backend; this page only presents them.
*/

export default function DashboardPage() {
  const dashboard = useApiGet<DashboardResponse>(API_ROUTES.dashboard);
  const currency = useCurrency();
  const summary = dashboard.data?.summary ?? null;

  // A dashboard with zero products is treated as "no data yet" rather than
  // healthy-everything, so the owner is not misled.
  const hasProducts =
    summary != null &&
    summary.items_needing_attention +
      summary.healthy_items +
      summary.unavailable_items >
      0;

  // AI loads only after the deterministic data is settled, so slow or failed
  // Gemini can never block the Dashboard.
  const brief = useApiGet<AIExplanationResponse>(
    API_ROUTES.aiBusinessBrief,
    !dashboard.loading && hasProducts,
  );
  const aiPending =
    brief.loading || (brief.data == null && brief.error == null);

  return (
    <PageContainer>
      <PageHeader
        title="Dashboard"
        description="Here's what needs your attention today."
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={dashboard.reload}
            disabled={dashboard.loading}
          >
            <Icon name="refresh" width={16} height={16} />
            Refresh
          </Button>
        }
      />

      {dashboard.loading ? (
        <LoadingState label="Loading dashboard">
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
            <Skeleton className="h-72 w-full" />
            <Skeleton className="h-40 w-full" />
          </div>
        </LoadingState>
      ) : dashboard.error ? (
        <ErrorState
          title="We couldn't load your dashboard"
          description={
            dashboard.error.kind === "network"
              ? "The InventoryIQ server didn't respond. Check that it is running, then try again."
              : "The server couldn't load your dashboard right now. Please try again."
          }
          onRetry={dashboard.reload}
        />
      ) : !summary || !hasProducts ? (
        <EmptyState
          icon="inbox"
          title="No inventory data yet"
          description="Once your products are available from the connected Google Sheet, your business overview will appear here."
          action={
            <Link
              href="/settings"
              className="inline-flex h-10 items-center rounded-lg bg-brand px-4 text-sm font-medium text-white transition-colors hover:bg-brand-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
            >
              Go to Settings
            </Link>
          }
        />
      ) : (
        <div className="space-y-6">
          <BusinessHealth
            itemsNeedingAttention={summary.items_needing_attention}
            healthyItems={summary.healthy_items}
            unavailableItems={summary.unavailable_items}
            totalInventoryValue={summary.total_inventory_value ?? null}
            currency={currency}
          />
          <TopPriorities priorities={summary.top_priorities ?? []} />
          <AiBusinessBrief
            loading={aiPending}
            data={brief.data}
            hasError={brief.error != null}
            onRetry={brief.reload}
          />
        </div>
      )}
    </PageContainer>
  );
}
