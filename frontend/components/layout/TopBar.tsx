"use client";

import { Icon } from "@/components/ui/icons";
import { GlobalSearch } from "./GlobalSearch";
import { MobileNav } from "./MobileNav";
import { useBusinessName } from "./SettingsProvider";

/**
 * Shared top bar. The search field submits into the Inventory page's
 * authoritative search; the bell is decorative (no notification system
 * exists) and the identity area is not an account control.
 */
export function TopBar() {
  const businessName = useBusinessName();

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-surface">
      <div className="flex h-16 items-center gap-4 px-4 sm:px-6 lg:px-8">
        <GlobalSearch />

        <div className="ml-auto flex items-center gap-3">
          <span
            className="flex h-9 w-9 items-center justify-center rounded-full text-ink-soft"
            aria-hidden="true"
          >
            <Icon name="bell" />
          </span>
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-soft text-brand">
              <Icon name="store" width={18} height={18} />
            </span>
            <span className="hidden text-sm font-medium text-ink sm:block">
              {businessName}
            </span>
            <Icon
              name="chevron-down"
              width={16}
              height={16}
              className="hidden text-muted sm:block"
            />
          </div>
        </div>
      </div>
      <MobileNav />
    </header>
  );
}
