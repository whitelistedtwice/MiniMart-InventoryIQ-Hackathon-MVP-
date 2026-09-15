"use client";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { Icon } from "@/components/ui/icons";
import { LoadingState, Skeleton } from "@/components/ui/LoadingState";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";
import { useSettings } from "@/components/layout/SettingsProvider";
import { formatDate } from "@/lib/format";

/*
  Settings (Phase 14, profile Phase 15, probe Phase 16).

  A lightweight, read-only presentation of `GET /api/v1/settings`: the
  configured business profile and the Google Sheets connection state.

  The business profile is environment configuration (single business, no
  database), so the page is intentionally read-only. `sheets_connection_state`
  is the result of a cached live probe, so the UI shows honest states:
  Not configured / Configured / Connected / Connection error (C-002).
*/

const MISSING = "—";

function SettingsSkeleton() {
  return (
    <LoadingState label="Loading settings">
      <div className="space-y-6">
        <Skeleton className="h-52 w-full" />
        <Skeleton className="h-44 w-full" />
      </div>
    </LoadingState>
  );
}

function InfoRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
      <dt className="text-sm font-medium text-ink-soft">{label}</dt>
      <dd className="text-sm text-ink">{value}</dd>
    </div>
  );
}

function BusinessProfileCard({
  businessName,
  businessType,
  currency,
  timezone,
}: {
  businessName: string | null | undefined;
  businessType: string | null | undefined;
  currency: string | null | undefined;
  timezone: string | null | undefined;
}) {
  return (
    <section aria-label="Business profile">
      <Card>
        <h2 className="text-lg font-semibold text-ink">Business Profile</h2>
        <p className="mt-0.5 text-sm text-muted">
          Basic information about your business. These values are set by your
          InventoryIQ configuration.
        </p>
        <dl className="mt-5 space-y-4">
          <InfoRow label="Business Name" value={businessName ?? MISSING} />
          <InfoRow label="Business Type" value={businessType ?? MISSING} />
          <InfoRow
            label="Currency"
            value={
              currency
                ? currency
                : `${MISSING} (money values are shown without a currency)`
            }
          />
          <InfoRow label="Timezone" value={timezone ?? MISSING} />
        </dl>
      </Card>
    </section>
  );
}

function ConnectionCard({
  state,
  error,
  lastSyncAt,
}: {
  state: string;
  error?: string | null;
  lastSyncAt: string | null | undefined;
}) {
  const labels: Record<string, string> = {
    not_configured: "Not configured",
    configured: "Configured",
    connected: "Connected",
    error: "Connection error",
  };
  const variants: Record<string, "neutral" | "success" | "danger"> = {
    not_configured: "neutral",
    configured: "neutral",
    connected: "success",
    error: "danger",
  };
  const hints: Record<string, string> = {
    not_configured: "Google Sheets credentials are not configured yet.",
    configured:
      "Credentials are configured; live connection not yet verified.",
    connected: "Google Sheets is reachable and the required tabs exist.",
    error: error ?? "InventoryIQ could not reach Google Sheets.",
  };

  return (
    <section aria-label="Google Sheets connection">
      <Card>
        <h2 className="text-lg font-semibold text-ink">
          Google Sheets Connection
        </h2>
        <p className="mt-0.5 text-sm text-muted">
          Where InventoryIQ reads your business data.
        </p>

        <div className="mt-5 space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <Badge variant={variants[state] ?? "neutral"}>
              {labels[state] ?? state}
            </Badge>
            <span className="text-sm text-muted">
              {hints[state] ?? ""}
            </span>
          </div>

          {state === "error" && error && (
            <p className="rounded-lg bg-danger-soft p-3 text-sm text-danger">
              {error}
            </p>
          )}

          <InfoRow
            label="Last sync"
            value={lastSyncAt ? formatDate(lastSyncAt) : MISSING}
          />
        </div>
      </Card>
    </section>
  );
}

export default function SettingsPage() {
  const { settings, loading, error, reload } = useSettings();

  if (loading) {
    return (
      <PageContainer>
        <PageHeader
          title="Settings"
          description="Manage your business profile and connected data."
        />
        <SettingsSkeleton />
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <PageHeader
          title="Settings"
          description="Manage your business profile and connected data."
        />
        <ErrorState
          title="We couldn't load your settings"
          description={
            error.kind === "network"
              ? "The InventoryIQ server didn't respond. Check that it is running, then try again."
              : "The server couldn't load your settings right now. Please try again."
          }
          onRetry={reload}
        />
      </PageContainer>
    );
  }

  if (!settings) {
    return (
      <PageContainer>
        <PageHeader
          title="Settings"
          description="Manage your business profile and connected data."
        />
        <ErrorState
          title="We couldn't load your settings"
          description="The server returned an unexpected response. Please try again."
          onRetry={reload}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Settings"
        description="Manage your business profile and connected data."
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={reload}
            disabled={loading}
          >
            <Icon name="refresh" width={16} height={16} />
            Refresh
          </Button>
        }
      />

      <div className="space-y-6">
        <BusinessProfileCard
          businessName={settings.business_name}
          businessType={settings.business_type}
          currency={settings.currency}
          timezone={settings.timezone}
        />
        <ConnectionCard
          state={settings.sheets_connection_state}
          error={settings.sheets_connection_error}
          lastSyncAt={settings.last_sync_at}
        />
      </div>
    </PageContainer>
  );
}
