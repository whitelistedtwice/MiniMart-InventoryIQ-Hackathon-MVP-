"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Icon } from "@/components/ui/icons";

/*
  Global top-bar search (C-022).

  There is exactly ONE product-search implementation: the Inventory page.
  This field does not keep its own search state — submitting it simply
  navigates to Inventory with a `q` query, which the Inventory page applies.
*/

export function GlobalSearch() {
  const router = useRouter();
  const [value, setValue] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = value.trim();
    router.push(
      query ? `/inventory?q=${encodeURIComponent(query)}` : "/inventory",
    );
  }

  return (
    <form
      role="search"
      onSubmit={submit}
      className="relative hidden w-full max-w-md sm:block"
    >
      <label htmlFor="global-search" className="sr-only">
        Search products
      </label>
      <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted">
        <Icon name="search" width={18} height={18} />
      </span>
      <input
        id="global-search"
        type="search"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Search products, categories…"
        className="h-10 w-full rounded-lg border border-line bg-canvas pl-10 pr-3 text-sm text-ink placeholder:text-muted focus:border-brand focus:bg-surface focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
      />
    </form>
  );
}
