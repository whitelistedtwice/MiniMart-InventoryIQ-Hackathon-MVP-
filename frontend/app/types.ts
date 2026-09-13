/**
 * Frontend API contracts.
 *
 * These types mirror the backend contracts in `backend/app/contracts/`.
 * The frontend consumes backend responses directly and does not
 * recompute business metrics.
 */

// -------------------------------------------------------------------------
// Source-data shapes (mirrors Google Sheets tabs)
// -------------------------------------------------------------------------

export interface Product {
  product_id: string;
  product_name: string;
  category?: string | null;
  unit?: string | null;
  unit_cost?: number | null;
  selling_price?: number | null;
  supplier?: string | null;
  lead_time_days?: number | null;
  target_stock_days?: number | null;
}

export interface Sale {
  date: string; // ISO date
  product_id: string;
  quantity_sold: number;
}

export interface InventorySnapshot {
  date: string;
  product_id: string;
  quantity_on_hand: number;
}

export interface Shipment {
  shipment_id: string;
  product_id: string;
  quantity: number;
  expected_arrival: string;
}

// -------------------------------------------------------------------------
// Recommendation contract
// -------------------------------------------------------------------------

export type RecommendationAction =
  | "REORDER"
  | "REDUCE EXCESS"
  | "MONITOR / PREPARE"
  | "NO ACTION"
  | "UNAVAILABLE";

export interface RecommendationResult {
  product_id: string;
  product_name: string;
  action: RecommendationAction;
  priority: number;
  reorder_quantity?: number | null;
  reorder_timing?: string | null;
  incoming_stock_sufficient?: boolean | null;
  evidence: string[];
  current_stock?: number | null;
  incoming_quantity?: number | null;
  days_of_stock_remaining?: number | null;
  days_until_arrival?: number | null;
  demand_trend?: DemandTrend;
  target_stock_days?: number | null;
  excess_units?: number | null;
}

// -------------------------------------------------------------------------
// Analytics contract
// -------------------------------------------------------------------------

export type DemandTrend = "increasing" | "stable" | "decreasing" | "unavailable";

export interface DemandMetrics {
  total_sold?: number | null;
  average_daily_sales?: number | null;
  recent_daily_sales?: number | null;
  trend: DemandTrend;
}

export interface InventoryMetrics {
  current_stock?: number | null; // null means unavailable, not zero
  inventory_value?: number | null;
  days_of_stock_remaining?: number | null;
  stock_status?: string | null; // 'low' | 'healthy' | 'excess' | null
  stockout_risk?: boolean | null; // null when undeterminable
  excess_units?: number | null;
  excess_value?: number | null;
}

export interface ShipmentProjection {
  incoming_quantity?: number | null;
  expected_arrival?: string | null;
  days_until_arrival?: number | null;
  expected_future_inventory?: number | null; // current + incoming, convenience only
  stockout_before_arrival?: boolean | null;
}

export interface FinancialMetrics {
  revenue?: number | null;
  estimated_cost?: number | null;
  profit?: number | null;
  profit_margin?: number | null;
  financial_exposure?: number | null;
}

export interface ProductAnalytics {
  product_id: string;
  product_name: string;
  demand: DemandMetrics;
  inventory: InventoryMetrics;
  shipment: ShipmentProjection;
  financial: FinancialMetrics;
  sales_history: Array<[string, number]>;
  inventory_history: Array<[string, number]>;
}

// -------------------------------------------------------------------------
// Verified AI context
// -------------------------------------------------------------------------

export interface AIProductContext {
  product_id: string;
  product_name: string;
  category?: string | null;
  current_stock?: number | null;
  demand_trend: DemandTrend;
  average_daily_sales?: number | null;
  days_of_stock_remaining?: number | null;
  incoming_quantity?: number | null;
  incoming_arrival_days?: number | null;
  recommendation_action: RecommendationAction;
  priority: number;
  recommended_reorder_quantity?: number | null;
  reorder_timing?: string | null;
  target_stock_days?: number | null;
  excess_units?: number | null;
  inventory_value?: number | null;
  financial_exposure?: number | null;
  evidence: string[];
}

export interface AIBusinessBriefContext {
  generated_at: string;
  total_inventory_value?: number | null;
  items_needing_attention: number;
  healthy_items: number;
  top_priorities: AIProductContext[];
}

export interface AIRecommendationContext {
  generated_at: string;
  product: AIProductContext;
}

export interface AIInsightContext {
  generated_at: string;
  focus_area: string;
  verified_trends: string[];
  product_highlights: AIProductContext[];
}

// -------------------------------------------------------------------------
// API response contracts
// -------------------------------------------------------------------------

export interface ProductListItem {
  product_id: string;
  product_name: string;
  category?: string | null;
  current_stock?: number | null;
  status: RecommendationAction;
  days_remaining?: number | null;
}

export interface DashboardSummary {
  items_needing_attention: number;
  healthy_items: number;
  total_inventory_value?: number | null;
  top_priorities: ProductListItem[];
}

export interface DashboardResponse {
  generated_at: string;
  summary: DashboardSummary;
  ai_brief_context: AIBusinessBriefContext;
}

export interface ProductDetailResponse {
  product_id: string;
  analytics: ProductAnalytics;
  recommendation: RecommendationResult;
  ai_context: AIRecommendationContext;
  historical_inventory: Array<[string, number]>;
}

export interface AnalyticsResponse {
  generated_at: string;
  products: ProductAnalytics[];
  ai_insight_context: AIInsightContext;
}

export interface SettingsResponse {
  business_name?: string | null;
  business_type?: string | null;
  sheets_connected: boolean;
  last_sync_at?: string | null;
}

export interface AIExplanationResponse {
  summary: string;
  reason?: string | null;
  action_explanation?: string | null;
  future_note?: string | null;
  ai_available: boolean;
}

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown> | null;
}
