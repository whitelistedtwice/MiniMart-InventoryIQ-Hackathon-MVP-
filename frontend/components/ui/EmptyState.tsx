import type { ReactNode } from "react";
import { Card } from "./Card";
import { Icon, type IconName } from "./icons";

type EmptyStateProps = {
  title: string;
  description?: string;
  icon?: IconName;
  action?: ReactNode;
};

/** Shared empty / insufficient-data foundation. */
export function EmptyState({
  title,
  description,
  icon = "inbox",
  action,
}: EmptyStateProps) {
  return (
    <Card className="flex flex-col items-center gap-3 py-12 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-brand-soft text-brand">
        <Icon name={icon} />
      </span>
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      {description ? (
        <p className="max-w-md text-sm text-muted">{description}</p>
      ) : null}
      {action ? <div className="mt-1">{action}</div> : null}
    </Card>
  );
}
