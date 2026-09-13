"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon } from "@/components/ui/icons";
import { NAV_ITEMS } from "./nav-items";

/** Compact navigation shown below the top bar on smaller screens. */
export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-1 overflow-x-auto border-t border-line bg-surface px-3 py-2 lg:hidden">
      {NAV_ITEMS.map((item) => {
        const active =
          pathname === item.href || pathname.startsWith(`${item.href}/`);
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              active
                ? "bg-brand-soft text-brand-strong"
                : "text-ink-soft hover:bg-canvas hover:text-ink"
            }`}
          >
            <Icon name={item.icon} width={18} height={18} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
