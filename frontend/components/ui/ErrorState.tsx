"use client";

import { Card } from "./Card";
import { Button } from "./Button";
import { Icon } from "./icons";

type ErrorStateProps = {
  title?: string;
  description?: string;
  onRetry?: () => void;
  retryLabel?: string;
};

/**
 * Shared error foundation. Shows a friendly message only — never raw
 * exceptions, stack traces, credentials, or infrastructure details.
 */
export function ErrorState({
  title = "Something went wrong",
  description = "We couldn't load this right now. Please try again.",
  onRetry,
  retryLabel = "Try again",
}: ErrorStateProps) {
  return (
    <Card className="flex flex-col items-center gap-3 py-12 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-danger-soft text-danger">
        <Icon name="alert" />
      </span>
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      <p className="max-w-md text-sm text-muted">{description}</p>
      {onRetry ? (
        <Button variant="secondary" size="sm" onClick={onRetry} className="mt-1">
          <Icon name="refresh" width={16} height={16} />
          {retryLabel}
        </Button>
      ) : null}
    </Card>
  );
}
