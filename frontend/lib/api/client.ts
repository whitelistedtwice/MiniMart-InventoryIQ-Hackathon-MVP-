import { API_BASE_URL } from "./config";

/**
 * Frontend API client foundation.
 *
 * Distinguishes the failure modes the UI must handle: a network failure, a
 * backend error, and an invalid response. It never surfaces raw backend
 * exceptions, stack traces, or infrastructure details — callers branch on
 * `kind` and show a friendly state.
 */
export type ApiErrorKind = "network" | "server" | "invalid";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly code?: string;

  constructor(
    kind: ApiErrorKind,
    message: string,
    options?: { status?: number; code?: string },
  ) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = options?.status;
    this.code = options?.code;
  }
}

const MESSAGES: Record<ApiErrorKind, string> = {
  network: "We couldn't reach the InventoryIQ server.",
  server: "The server couldn't complete this request.",
  invalid: "The server returned an unexpected response.",
};

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      method: "GET",
      headers: { Accept: "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError("network", MESSAGES.network);
  }

  if (!response.ok) {
    let code: string | undefined;
    try {
      const body = (await response.json()) as { error?: unknown };
      if (typeof body?.error === "string") code = body.error;
    } catch {
      // Non-JSON error body — keep the generic server message.
    }
    throw new ApiError("server", MESSAGES.server, {
      status: response.status,
      code,
    });
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError("invalid", MESSAGES.invalid);
  }
}
