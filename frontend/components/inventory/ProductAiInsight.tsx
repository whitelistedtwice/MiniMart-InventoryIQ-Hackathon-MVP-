"use client";

import { useState } from "react";

import type { AIExplanationResponse } from "@/app/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Icon } from "@/components/ui/icons";
import { Skeleton } from "@/components/ui/LoadingState";
import { useApiGet } from "@/lib/api/hooks";
import { API_ROUTES } from "@/lib/api/routes";

/*
  AI Product Insight.

  Collapsed until the owner asks for it, so Gemini never blocks or delays
  the deterministic Product Detail. The response is validated backend
  output; failure shows a friendly fallback, never raw errors or fake text.
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

export function ProductAiInsight({ productId }: { productId: string }) {
  const [open, setOpen] = useState(false);
  const ai = useApiGet<AIExplanationResponse>(
    API_ROUTES.aiRecommendation(productId),
    open,
  );

  const pending = ai.loading || (ai.data == null && ai.error == null);
  const available =
    !ai.error && ai.data != null && ai.data.ai_available && !!ai.data.summary;

  return (
    <Card className="border-ai-line bg-ai-soft">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-surface text-ai ring-1 ring-ai-line"
            aria-hidden="true"
          >
            <Icon name="sparkles" width={18} height={18} />
          </span>
          <div>
            <h2 className="text-base font-semibold text-ink">
              AI Product Insight
            </h2>
            <p className="text-xs text-muted">
              Gemini explains the verified recommendation.
            </p>
          </div>
        </div>

        {open ? (
          <Button variant="secondary" size="sm" onClick={() => setOpen(false)}>
            Collapse
          </Button>
        ) : null}
      </div>

      <div className="mt-4">
        {!open ? (
          <Button size="sm" onClick={() => setOpen(true)}>
            <Icon name="sparkles" width={16} height={16} />
            See What AI Recommends
          </Button>
        ) : pending ? (
          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ) : available && ai.data ? (
          <div className="space-y-4">
            <p className="text-sm leading-relaxed text-ink">
              {ai.data.summary}
            </p>
            {ai.data.reason ? (
              <Section label="Why this recommendation?" text={ai.data.reason} />
            ) : null}
            {ai.data.action_explanation ? (
              <Section
                label="Recommended action"
                text={ai.data.action_explanation}
              />
            ) : null}
            {ai.data.future_note ? (
              <Section label="Additional note" text={ai.data.future_note} />
            ) : null}
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-ink-soft">
              AI insight is unavailable right now. The recommendation above is
              still the verified InventoryIQ result.
            </p>
            <Button variant="secondary" size="sm" onClick={ai.reload}>
              <Icon name="refresh" width={16} height={16} />
              Try again
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}
