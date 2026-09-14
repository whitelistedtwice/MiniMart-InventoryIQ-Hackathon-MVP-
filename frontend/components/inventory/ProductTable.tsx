import Link from "next/link";

import type { ProductListItem } from "@/app/types";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatDays, formatStock } from "@/lib/format";

/*
  Inventory product table.

  Renders exactly the fields from the `/api/v1/inventory` contract. Statuses
  come from the backend recommendation engine; missing values show "—" and
  are never converted to 0.
*/

const HEADERS = ["Product", "Category", "Current Stock", "Status", "Days Left"];

export function ProductTable({ products }: { products: ProductListItem[] }) {
  return (
    <Card padded={false} className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
              {HEADERS.map((header) => (
                <th key={header} scope="col" className="px-5 py-3 font-medium">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {products.map((product) => (
              <tr
                key={product.product_id}
                className="transition-colors hover:bg-canvas"
              >
                <td className="px-5 py-3.5">
                  <Link
                    href={`/inventory/${encodeURIComponent(product.product_id)}`}
                    className="font-medium text-ink hover:text-brand-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
                  >
                    {product.product_name}
                  </Link>
                </td>
                <td className="px-5 py-3.5 text-ink-soft">
                  {product.category ?? "—"}
                </td>
                <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                  {formatStock(product.current_stock)}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={product.status} />
                </td>
                <td className="px-5 py-3.5 tabular-nums text-ink-soft">
                  {formatDays(product.days_remaining)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
