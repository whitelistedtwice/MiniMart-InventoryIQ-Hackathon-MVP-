"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon } from "@/components/ui/icons";
import { NAV_ITEMS } from "./nav-items";

export function Sidebar({ businessName }: { businessName: string }) {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col border-r border-line bg-surface lg:flex">
      <div className="flex h-16 items-center px-5">
        <span className="text-lg font-bold tracking-tight text-ink">
          Inventory<span className="text-brand">IQ</span>
        </span>
      </div>

      <div className="mx-3 mb-3 flex items-center gap-3 rounded-lg bg-canvas px-3 py-2.5">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-soft text-brand">
          <Icon name="store" width={18} height={18} />
        </span>
        <span className="min-w-0 truncate text-sm font-medium text-ink">
          {businessName}
        </span>
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-3">
        {NAV_ITEMS.map((item) => {
          const active =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={`flex items-center gap-3 rounded-lg border-l-2 px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "border-brand bg-brand-soft text-brand-strong"
                  : "border-transparent text-ink-soft hover:bg-canvas hover:text-ink"
              }`}
            >
              <Icon name={item.icon} width={18} height={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="px-5 py-4 text-xs text-muted">InventoryIQ MVP</div>
    </aside>
  );
}
