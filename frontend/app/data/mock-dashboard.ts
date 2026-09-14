export type MockPriorityStatus =
  | "REORDER"
  | "REDUCE EXCESS"
  | "MONITOR / PREPARE"
  | "NO ACTION"
  | "UNAVAILABLE";

export type MockKpiTone = "danger" | "success" | "brand";

export type MockKpi = {
  icon: "alert" | "check" | "coins";
  tone: MockKpiTone;
  value: string;
  label: string;
  hint: string;
  badge: string;
};

export type MockQuickActionVariant = "primary" | "secondary" | "ghost";

export type MockDashboardViewModel = {
  businessName: string;
  summary: string;
  lastUpdated: string;
  kpis: MockKpi[];
  priorities: Array<{
    product_id: string;
    product_name: string;
    category: string;
    current_stock: number;
    days_remaining: number;
    status: MockPriorityStatus;
  }>;
  recentActivity: Array<{
    title: string;
    detail: string;
    time: string;
    tone: "success" | "brand" | "warning" | "neutral";
  }>;
  trend: number[];
  stockStatus: Array<{
    label: string;
    value: number;
    count: number;
    tone: "success" | "danger" | "warning";
  }>;
  shipments: Array<{
    product: string;
    eta: string;
    qty: string;
    status: string;
    tone: "brand" | "success" | "warning";
  }>;
  quickActions: Array<{
    label: string;
    icon: "refresh" | "alert" | "arrow-right";
    variant: MockQuickActionVariant;
  }>;
};
