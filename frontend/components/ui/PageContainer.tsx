import type { ReactNode } from "react";

/** Shared page width and padding used by every page. */
export function PageContainer({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-4 py-6 sm:px-6 lg:px-8">
      {children}
    </div>
  );
}
