"use client";

import type { AIExplanationResponse } from "@/app/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Icon } from "@/components/ui/icons";
import { Skeleton } from "@/components/ui/LoadingState";

/*
  AI Business Brief.

  Gemini is an explanation layer only. The deterministic Dashboard renders
  independently of this card; when AI is slow, unavailable, or returns no
  usable content, a friendly fallback is shown instead of raw errors or
  fabricated text.
*/

function Section({ label, text }: { label: string; text: string }) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wide text-ai">
        {label}
      </h3>
      <p className="mt-1 text-sm leading-relaxed text-ink-soft">{text}</p>
    </div>
  );
}

export function AiBusinessBrief({
  loading,
  data,
  hasError,
  onRetry,
}: {
  loading: boolean;
  data: AIExplanationResponse | null;
  hasError: boolean;
  onRetry: () => void;
}) {
  const available =
    !hasError && data != null && data.ai_available && !!data.summary;

  return (
    <Card className="border-ai-line bg-ai-soft">
      <div className="flex items-center gap-3">
        <span
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-surface text-ai ring-1 ring-ai-line"
          aria-hidden="true"
        >
          <Icon name="sparkles" width={18} height={18} />
        </span>
        <div>
          <h2 className="text-base font-semibold text-ink">
            AI Business Brief
          </h2>
          <p className="text-xs text-muted">
            Your daily overview powered by AI.
          </p>
        </div>
      </div>

      <div className="mt-4">
        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-11/12" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ) : available && data ? (
          <div className="space-y-4">
            <p className="text-sm leading-relaxed text-ink">
              {data.summary}
            </p>
            {data.reason ? <Section label="Why" text={data.reason} /> : null}
            {data.action_explanation ? (
              <Section
                label="Recommended action"
                text={data.action_explanation}
              />
            ) : null}
            {data.future_note ? (
              <Section label="What to watch" text={data.future_note} />
            ) : null}
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-ink-soft">
              AI explanation is unavailable right now. Your inventory data is
              still up to date.
            </p>
            <Button variant="secondary" size="sm" onClick={onRetry}>
              <Icon name="refresh" width={16} height={16} />
              Try again
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}
