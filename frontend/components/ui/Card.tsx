import type { HTMLAttributes } from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  /** Add the default inner padding. Set false for flush content like tables. */
  padded?: boolean;
};

export function Card({ padded = true, className = "", ...props }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-line bg-surface shadow-sm ${
        padded ? "p-5" : ""
      } ${className}`}
      {...props}
    />
  );
}
