import type { ReactNode } from "react";

import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

/**
 * Shared application shell: persistent sidebar + top bar + main content.
 *
 * `businessName` is a display value owned by the backend in later phases.
 * Until Settings provides it, a neutral label is shown — never a fabricated
 * business identity.
 */
export function AppShell({
  children,
  businessName = "Your business",
}: {
  children: ReactNode;
  businessName?: string;
}) {
  return (
    <div className="min-h-screen">
      <Sidebar businessName={businessName} />
      <div className="flex min-h-screen flex-col lg:pl-60">
        <TopBar businessName={businessName} />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
