"use client";

import type { SettingsResponse } from "@/app/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { Icon } from "@/components/ui/icons";
import { LoadingState, Skeleton } from "@/components/ui/LoadingState";
import { PageContainer } from "@/components/ui/PageContainer";
import { PageHeader } from "@/components/ui/PageHeader";
import { useApiGet } from "@/lib/api/hooks";
import { API_ROUTES } from "@/lib/api/routes";
import { formatDate } from "@/lib/format";

/*
  Settings (Phase 14).

  A lightweight, read-only presentation of `GET /api/v1/settings`:
  business profile and Google Sheets connection state. The backend contract
  currently exposes only configuration-presence (`sheets_connected`) and does
  not support editing or live connectivity probing, so the UI is honest about
  that — it says "Configured" / "Not configured", never "Connected and working".

  No persistence, no credentials, no account management, no sync toggles.
*/

const MISSING = "—";

function SettingsSkeleton() {
  return (
    <LoadingState label="Loading settings">
      <div className="space-y-6">
        <Skeleton className="h-44 w-full" />
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

function BusinessProfileCard({ data }: { data: SettingsResponse }) {
  return (
    <section aria-label="Business profile">
      <Card>
        <h2 className="text-lg font-semibold text-ink">Business Profile</h2>
        <p className="mt-0.5 text-sm text-muted">
          Basic information about your business.
        </p>
        <dl className="mt-5 space-y-4">
          <InfoRow
            label="Business Name"
            value={data.business_name ?? MISSING}
          />
          <InfoRow
            label="Business Type"
            value={data.business_type ?? MISSING}
          />
        </dl>
      </Card>
    </section>
  );
}

function ConnectionCard({ data }: { data: SettingsResponse }) {
  const configured = data.sheets_connected;

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
            <Badge variant={configured ? "success" : "neutral"}>
              {configured ? "Configured" : "Not configured"}
            </Badge>
            <span className="text-sm text-muted">
              {configured
                ? "Google Sheets credentials are configured."
                : "Google Sheets credentials are not configured yet."}
            </span>
          </div>

          <InfoRow
            label="Last sync"
            value={data.last_sync_at ? formatDate(data.last_sync_at) : MISSING}
          />
        </div>
      </Card>
    </section>
  );
}

export default function SettingsPage() {
  const settings = useApiGet<SettingsResponse>(API_ROUTES.settings);

  if (settings.loading) {
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

  if (settings.error) {
    return (
      <PageContainer>
        <PageHeader
          title="Settings"
          description="Manage your business profile and connected data."
        />
        <ErrorState
          title="We couldn't load your settings"
          description={
            settings.error.kind === "network"
              ? "The InventoryIQ server didn't respond. Check that it is running, then try again."
              : "The server couldn't load your settings right now. Please try again."
          }
          onRetry={settings.reload}
        />
      </PageContainer>
    );
  }

  const data = settings.data;
  if (!data) {
    return (
      <PageContainer>
        <PageHeader
          title="Settings"
          description="Manage your business profile and connected data."
        />
        <ErrorState
          title="We couldn't load your settings"
          description="The server returned an unexpected response. Please try again."
          onRetry={settings.reload}
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
            onClick={settings.reload}
            disabled={settings.loading}
          >
            <Icon name="refresh" width={16} height={16} />
            Refresh
          </Button>
        }
      />

      <div className="space-y-6">
        <BusinessProfileCard data={data} />
        <ConnectionCard data={data} />
      </div>
    </PageContainer>
  );
}
