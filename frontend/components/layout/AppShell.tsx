import type { ReactNode } from "react";

import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

/**
 * Shared application shell: persistent sidebar + top bar + main content.
 *
 * The business name is fetched by the shared SettingsProvider (backend
 * business profile) so every page shows the same identity without extra
 * requests; the shell falls back to a neutral label when it is unset.
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <Sidebar />
      <div className="flex min-h-screen flex-col lg:pl-60">
        <TopBar />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
