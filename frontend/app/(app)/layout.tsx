import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { SettingsProvider } from "@/components/layout/SettingsProvider";

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <SettingsProvider>
      <AppShell>{children}</AppShell>
    </SettingsProvider>
  );
}
