"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, apiGet } from "./client";

/*
  Small client-side data hook built on the shared API client.

  It clears stale data when a request restarts, ignores responses from
  unmounted/outdated requests, and exposes a `reload` for retry/refresh.
  All failures are normalised to ApiError so callers can render a friendly
  state without ever seeing raw backend errors.
*/

export type ApiGetState<T> = {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
};

export function useApiGet<T>(path: string, enabled = true) {
  const [state, setState] = useState<ApiGetState<T>>({
    data: null,
    error: null,
    loading: enabled,
  });
  const [reloadKey, setReloadKey] = useState(0);

  const reload = useCallback(() => setReloadKey((key) => key + 1), []);

  useEffect(() => {
    if (!enabled) {
      setState({ data: null, error: null, loading: false });
      return;
    }

    let active = true;
    setState({ data: null, error: null, loading: true });

    apiGet<T>(path)
      .then((data) => {
        if (active) setState({ data, error: null, loading: false });
      })
      .catch((error: unknown) => {
        if (!active) return;
        setState({
          data: null,
          loading: false,
          error:
            error instanceof ApiError
              ? error
              : new ApiError(
                  "invalid",
                  "The server returned an unexpected response.",
                ),
        });
      });

    return () => {
      active = false;
    };
  }, [path, enabled, reloadKey]);

  return { ...state, reload };
}
