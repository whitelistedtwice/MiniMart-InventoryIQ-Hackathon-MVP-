/** Low-level shimmer block used to build loading skeletons. */
export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-md bg-line/70 ${className}`}
      aria-hidden="true"
    />
  );
}

/**
 * Shared loading foundation. Callers control the skeleton shape; this keeps
 * the card structure visible without ever showing fake business data.
 */
export function LoadingState({
  label = "Loading…",
  children,
}: {
  label?: string;
  children?: React.ReactNode;
}) {
  return (
    <div role="status" aria-live="polite" aria-label={label}>
      {children ?? (
        <div className="space-y-4">
          <Skeleton className="h-6 w-48" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
          <Skeleton className="h-48 w-full" />
        </div>
      )}
      <span className="sr-only">{label}</span>
    </div>
  );
}
