"use client";

import { createContext, useContext, type ReactNode } from "react";

import type { SettingsResponse } from "@/app/types";
import type { ApiError } from "@/lib/api/client";
import { useApiGet } from "@/lib/api/hooks";
import { API_ROUTES } from "@/lib/api/routes";

/*
  Shared settings data (Phase 15).

  The business profile is fetched once per app load and shared by the shell
  (business name) and every consumer that needs the configured currency.
  One request, one source of truth: pages never fetch settings independently.

  A failed or slow settings request never blocks the app — the shell falls
  back to neutral labels and money renders without a currency until the
  backend says otherwise.
*/

type SettingsContextValue = {
  settings: SettingsResponse | null;
  loading: boolean;
  error: ApiError | null;
  reload: () => void;
};

const SettingsContext = createContext<SettingsContextValue | null>(null);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const { data, error, loading, reload } = useApiGet<SettingsResponse>(
    API_ROUTES.settings,
  );

  return (
    <SettingsContext.Provider
      value={{ settings: data, loading, error, reload }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings(): SettingsContextValue {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within SettingsProvider");
  }
  return context;
}

/** Business name for the shell; a safe neutral fallback when unset. */
export function useBusinessName(): string {
  const { settings } = useSettings();
  return settings?.business_name ?? "Your business";
}

/** Configured money currency (ISO 4217), or null when not configured. */
export function useCurrency(): string | null {
  const { settings } = useSettings();
  return settings?.currency ?? null;
}
