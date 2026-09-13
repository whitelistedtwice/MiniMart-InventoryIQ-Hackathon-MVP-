import Link from "next/link";

import type { ProductListItem } from "@/app/types";
import { Card } from "@/components/ui/Card";
import { Icon } from "@/components/ui/icons";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDays, formatStock } from "./format";

/*
  Top Priorities.

  Renders the backend's deterministic ordering and statuses verbatim.
  The frontend does not rank, recalculate, or reinterpret anything.
  Product Detail is a later phase, so items link to the Inventory list
  ("View all") rather than to a route that does not exist yet.
*/

function PriorityRow({ item }: { item: ProductListItem }) {
  return (
    <li className="flex flex-wrap items-center gap-x-4 gap-y-2 px-5 py-3.5">
      <div className="min-w-0 flex-1 basis-48">
        <p className="truncate text-sm font-medium text-ink">
          {item.product_name}
        </p>
        {item.category ? (
          <p className="truncate text-xs text-muted">{item.category}</p>
        ) : null}
      </div>

      <StatusBadge status={item.status} />

      <div className="flex gap-6">
        <div className="w-16">
          <p className="text-[11px] uppercase tracking-wide text-muted">
            Stock
          </p>
          <p className="text-sm tabular-nums text-ink-soft">
            {formatStock(item.current_stock)}
          </p>
        </div>
        <div className="w-24">
          <p className="text-[11px] uppercase tracking-wide text-muted">
            Days left
          </p>
          <p className="text-sm tabular-nums text-ink-soft">
            {formatDays(item.days_remaining)}
          </p>
        </div>
      </div>
    </li>
  );
}

export function TopPriorities({
  priorities,
}: {
  priorities: ProductListItem[];
}) {
  return (
    <Card padded={false}>
      <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
        <div className="flex items-center gap-2">
          <span className="text-danger" aria-hidden="true">
            <Icon name="alert" width={18} height={18} />
          </span>
          <h2 className="text-base font-semibold text-ink">Top Priorities</h2>
        </div>
        <Link
          href="/inventory"
          className="inline-flex items-center gap-1 rounded text-sm font-medium text-brand hover:text-brand-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
        >
          View all
          <Icon name="arrow-right" width={16} height={16} />
        </Link>
      </div>

      {priorities.length === 0 ? (
        <p className="px-5 py-8 text-center text-sm text-muted">
          Nothing needs attention right now.
        </p>
      ) : (
        <ul className="divide-y divide-line">
          {priorities.map((item) => (
            <PriorityRow key={item.product_id} item={item} />
          ))}
        </ul>
      )}
    </Card>
  );
}
