import { Card } from "@/components/ui/Card";
import { Icon, type IconName } from "@/components/ui/icons";
import { formatCount, formatMoney } from "./format";

/*
  Business health indicators.

  Transparent backend counts only — no score, no percentage, no frontend
  calculation. `total_inventory_value` is Optional in the backend contract:
  null means unavailable and is shown as such, never as 0.
*/

type Tone = "danger" | "success" | "brand";

const TONES: Record<Tone, string> = {
  danger: "bg-danger-soft text-danger",
  success: "bg-success-soft text-success",
  brand: "bg-brand-soft text-brand",
};

function MetricCard({
  icon,
  tone,
  value,
  label,
  hint,
}: {
  icon: IconName;
  tone: Tone;
  value: string;
  label: string;
  hint: string;
}) {
  return (
    <Card className="flex items-start gap-4">
      <span
        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${TONES[tone]}`}
        aria-hidden="true"
      >
        <Icon name={icon} />
      </span>
      <div className="min-w-0">
        <p className="text-2xl font-semibold tabular-nums text-ink">{value}</p>
        <p className="text-sm font-medium text-ink-soft">{label}</p>
        <p className="mt-0.5 text-xs text-muted">{hint}</p>
      </div>
    </Card>
  );
}

export function BusinessHealth({
  itemsNeedingAttention,
  healthyItems,
  totalInventoryValue,
}: {
  itemsNeedingAttention: number;
  healthyItems: number;
  totalInventoryValue: number | null;
}) {
  const valueAvailable = totalInventoryValue != null;

  return (
    <section
      aria-label="Business health"
      className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
    >
      <MetricCard
        icon="alert"
        tone="danger"
        value={formatCount(itemsNeedingAttention)}
        label="Need Attention"
        hint="Products with a recommended action"
      />
      <MetricCard
        icon="check"
        tone="success"
        value={formatCount(healthyItems)}
        label="Healthy"
        hint="Products with no action needed"
      />
      <MetricCard
        icon="coins"
        tone="brand"
        value={formatMoney(totalInventoryValue)}
        label="Total Inventory Value"
        hint={
          valueAvailable
            ? "Across all products"
            : "Unavailable — some costs are missing"
        }
      />
    </section>
  );
}
