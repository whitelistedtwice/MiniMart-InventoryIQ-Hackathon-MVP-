import type { HTMLAttributes } from "react";

export type BadgeVariant =
  | "neutral"
  | "brand"
  | "success"
  | "danger"
  | "excess"
  | "warning"
  | "ai";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  variant?: BadgeVariant;
};

const VARIANTS: Record<BadgeVariant, string> = {
  neutral: "bg-canvas text-ink-soft border-line",
  brand: "bg-brand-soft text-brand-strong border-brand-soft",
  success: "bg-success-soft text-success border-success-soft",
  danger: "bg-danger-soft text-danger border-danger-soft",
  excess: "bg-excess-soft text-excess border-excess-soft",
  warning: "bg-warning-soft text-warning border-warning-soft",
  ai: "bg-ai-soft text-ai border-ai-line",
};

export function Badge({
  variant = "neutral",
  className = "",
  ...props
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${VARIANTS[variant]} ${className}`}
      {...props}
    />
  );
}
