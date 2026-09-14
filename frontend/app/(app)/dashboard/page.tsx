import Link from "next/link";

import { buildDashboardViewModel } from "@/app/data/cambodian-demo-adapter";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Icon } from "@/components/ui/icons";
import { PageContainer } from "@/components/ui/PageContainer";
import { StatusBadge } from "@/components/ui/StatusBadge";

const toneClasses = {
  danger: "bg-danger-soft text-danger",
  success: "bg-success-soft text-success",
  brand: "bg-brand-soft text-brand",
  warning: "bg-warning-soft text-warning",
  neutral: "bg-canvas text-ink-soft",
} as const;

function KpiCard({
  icon,
  tone,
  value,
  label,
  hint,
  badge,
}: {
  icon: "alert" | "check" | "coins";
  tone: keyof typeof toneClasses;
  value: string;
  label: string;
  hint: string;
  badge: string;
}) {
  return (
    <Card className="flex h-full flex-col justify-between gap-4">
      <div className="flex items-start justify-between gap-3">
        <span
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${toneClasses[tone]}`}
          aria-hidden="true"
        >
          <Icon name={icon} width={18} height={18} />
        </span>
        <span className="text-[11px] font-medium uppercase tracking-[0.12em] text-muted">
          {badge}
        </span>
      </div>

      <div>
        <p className="text-3xl font-semibold tracking-tight text-ink">{value}</p>
        <p className="mt-1 text-sm font-medium text-ink-soft">{label}</p>
      </div>

      <p className="text-xs text-muted">{hint}</p>
    </Card>
  );
}

function TrendChart({ trend }: { trend: number[] }) {
  const points = trend
    .map((value: number, index: number) => {
      const x = 12 + index * 28;
      const y = 128 - value * 0.9;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="mt-5 overflow-hidden rounded-2xl border border-line bg-canvas p-3">
      <svg viewBox="0 0 320 150" className="h-40 w-full" role="img" aria-label="Inventory value trend over time">
        <defs>
          <linearGradient id="trendFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#2563eb" stopOpacity="0.18" />
            <stop offset="100%" stopColor="#2563eb" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0, 1, 2, 3].map((line) => (
          <line
            key={line}
            x1="0"
            x2="320"
            y1={20 + line * 35}
            y2={20 + line * 35}
            stroke="#dfe7f4"
            strokeDasharray="4 6"
          />
        ))}
        <polyline
          fill="none"
          stroke="#2563eb"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
        <polygon points={`12,128 ${points} 308,128`} fill="url(#trendFill)" opacity="0.9" />
      </svg>
    </div>
  );
}

export default function DashboardPage() {
  const dashboard = buildDashboardViewModel();
  const { businessName, summary, lastUpdated, kpis, priorities, recentActivity, stockStatus, shipments, quickActions } = dashboard;

  return (
    <PageContainer>
      <header className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-medium text-brand">Good morning</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight text-ink">
            {businessName}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-sm text-muted">Last updated {lastUpdated}</div>
          <Button variant="secondary" size="sm">
            <Icon name="refresh" width={16} height={16} />
            Refresh
          </Button>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {kpis.map((item) => (
          <KpiCard key={item.label} {...item} />
        ))}
      </section>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.5fr_0.9fr]">
        <div className="space-y-6">
          <Card padded={false}>
            <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
              <div className="flex items-center gap-2">
                <span className="text-danger" aria-hidden="true">
                  <Icon name="alert" width={18} height={18} />
                </span>
                <h2 className="text-base font-semibold text-ink">Top Priorities</h2>
              </div>
              <Link href="/inventory" className="inline-flex items-center gap-1 text-sm font-medium text-brand hover:text-brand-strong">
                View all
                <Icon name="arrow-right" width={16} height={16} />
              </Link>
            </div>

            <div className="overflow-hidden">
              <div className="grid grid-cols-[1.7fr_0.8fr_0.7fr_0.7fr] gap-4 border-b border-line bg-canvas px-5 py-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">
                <span>Product</span>
                <span>Status</span>
                <span>Stock</span>
                <span>Days</span>
              </div>
              <ul className="divide-y divide-line">
                {priorities.map((item) => (
                  <li key={item.product_id} className="grid grid-cols-[1.7fr_0.8fr_0.7fr_0.7fr] items-center gap-4 px-5 py-3.5">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-ink">{item.product_name}</p>
                      <p className="truncate text-xs text-muted">{item.category}</p>
                    </div>
                    <StatusBadge status={item.status} />
                    <div className="text-sm tabular-nums text-ink-soft">{item.current_stock}</div>
                    <div className="text-sm tabular-nums text-ink-soft">{item.days_remaining}d</div>
                  </li>
                ))}
              </ul>
            </div>
          </Card>

          <Card className="bg-ai-soft/40">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ai-soft text-ai">
                  <Icon name="sparkles" width={16} height={16} />
                </span>
                <h2 className="text-base font-semibold text-ink">AI Business Brief</h2>
              </div>
              <Badge variant="ai">Verified</Badge>
            </div>

            <p className="mt-4 text-sm leading-6 text-ink-soft">{summary}</p>

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <div className="rounded-xl border border-ai-line bg-surface p-3">
                <p className="text-[11px] uppercase tracking-[0.12em] text-muted">Focus</p>
                <p className="mt-2 text-sm font-medium text-ink">High-volume beans</p>
              </div>
              <div className="rounded-xl border border-ai-line bg-surface p-3">
                <p className="text-[11px] uppercase tracking-[0.12em] text-muted">Action</p>
                <p className="mt-2 text-sm font-medium text-ink">Reorder by Friday</p>
              </div>
              <div className="rounded-xl border border-ai-line bg-surface p-3">
                <p className="text-[11px] uppercase tracking-[0.12em] text-muted">Risk</p>
                <p className="mt-2 text-sm font-medium text-ink">Low with arrivals</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-ink">Inventory Value Trend</h2>
              <Badge variant="brand">This quarter</Badge>
            </div>
            <TrendChart trend={dashboard.trend} />
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-ink">Recent Activity</h2>
              <Link href="/analytics" className="text-sm font-medium text-brand hover:text-brand-strong">View all</Link>
            </div>

            <ul className="mt-4 space-y-3">
              {recentActivity.map((item) => (
                <li key={item.title} className="flex gap-3 rounded-xl border border-line bg-canvas px-3 py-2.5">
                  <span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${
                    item.tone === "success" ? "bg-success" :
                    item.tone === "brand" ? "bg-brand" :
                    item.tone === "warning" ? "bg-warning" : "bg-muted"
                  }`} aria-hidden="true" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-medium text-ink">{item.title}</p>
                      <span className="text-[11px] text-muted">{item.time}</span>
                    </div>
                    <p className="mt-1 text-xs text-muted">{item.detail}</p>
                  </div>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-ink">Stock Status Overview</h2>
              <span className="text-xs text-muted">Live snapshot</span>
            </div>

            <div className="mt-5 space-y-4">
              {stockStatus.map((entry) => (
                <div key={entry.label}>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <span className="font-medium text-ink-soft">{entry.label}</span>
                    <span className="text-muted">{entry.count} items</span>
                  </div>
                  <div className="h-2.5 overflow-hidden rounded-full bg-canvas">
                    <div
                      className={`h-full rounded-full ${
                        entry.tone === "success" ? "bg-success" :
                        entry.tone === "danger" ? "bg-danger" : "bg-warning"
                      }`}
                      style={{ width: `${entry.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-ink">Upcoming Shipments</h2>
              <Link href="/inventory" className="text-sm font-medium text-brand hover:text-brand-strong">See all</Link>
            </div>

            <ul className="mt-4 space-y-3">
              {shipments.map((shipment) => (
                <li key={shipment.product} className="rounded-xl border border-line bg-canvas p-3.5">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-medium text-ink">{shipment.product}</p>
                    <Badge variant={shipment.tone === "brand" ? "brand" : shipment.tone === "success" ? "success" : "warning"}>{shipment.status}</Badge>
                  </div>
                  <p className="mt-2 text-xs text-muted">{shipment.eta}</p>
                  <p className="mt-1 text-sm font-medium text-ink-soft">{shipment.qty}</p>
                </li>
              ))}
            </ul>
          </Card>

          <Card>
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-ink">Quick Actions</h2>
            </div>

            <div className="mt-4 flex flex-col gap-2">
              {quickActions.map((action) => (
                <Button
                  key={action.label}
                  variant={action.variant}
                  className="justify-start"
                >
                  <Icon name={action.icon} width={16} height={16} />
                  {action.label}
                </Button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
