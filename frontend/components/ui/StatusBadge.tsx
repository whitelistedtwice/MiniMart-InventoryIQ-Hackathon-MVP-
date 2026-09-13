import type { RecommendationAction } from "@/app/types";
import { Badge, type BadgeVariant } from "./Badge";

/*
  Shared recommendation-status presentation.

  Maps the backend's RecommendationAction strings to the established
  InventoryIQ status colours. It does not calculate, change, or reinterpret
  the status — the backend owns the value.
*/

const STATUS: Record<RecommendationAction, BadgeVariant> = {
  REORDER: "danger",
  "REDUCE EXCESS": "excess",
  "MONITOR / PREPARE": "warning",
  "NO ACTION": "success",
  UNAVAILABLE: "neutral",
};

const LABELS: Record<RecommendationAction, string> = {
  REORDER: "Reorder",
  "REDUCE EXCESS": "Reduce Excess",
  "MONITOR / PREPARE": "Monitor / Prepare",
  "NO ACTION": "No Action",
  UNAVAILABLE: "Unavailable",
};

export function StatusBadge({ status }: { status: RecommendationAction }) {
  return <Badge variant={STATUS[status]}>{LABELS[status]}</Badge>;
}
