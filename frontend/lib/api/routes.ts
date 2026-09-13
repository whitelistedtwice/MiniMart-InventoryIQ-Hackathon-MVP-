/**
 * Existing backend API routes.
 *
 * Centralised so later phases reuse the same paths and never invent
 * duplicate endpoints. AI endpoints are called separately from the
 * deterministic ones so core data never waits on Gemini.
 */
export const API_ROUTES = {
  health: "/health",
  dashboard: "/api/v1/dashboard",
  inventory: "/api/v1/inventory",
  product: (productId: string) =>
    `/api/v1/inventory/${encodeURIComponent(productId)}`,
  analytics: "/api/v1/analytics",
  settings: "/api/v1/settings",
  aiBusinessBrief: "/api/v1/ai/business-brief",
  aiRecommendation: (productId: string) =>
    `/api/v1/ai/recommendation/${encodeURIComponent(productId)}`,
  aiInsight: "/api/v1/ai/insight",
} as const;
