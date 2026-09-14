import demoData from "./cambodian_mini_mart.json";

import type {
  MockDashboardViewModel,
  MockKpi,
  MockPriorityStatus,
  MockQuickActionVariant,
} from "./mock-dashboard";

type ProductRecord = {
  product_id: string;
  product_name: string;
  category?: string | null;
  unit_cost?: string | number | null;
  selling_price?: string | number | null;
  supplier?: string | null;
  lead_time_days?: string | number | null;
  target_stock_days?: string | number | null;
};

type SaleRecord = {
  date: string;
  product_id: string;
  quantity_sold: string | number;
};

type InventoryRecord = {
  date: string;
  product_id: string;
  quantity_on_hand: string | number;
};

type ShipmentRecord = {
  shipment_id: string;
  product_id: string;
  quantity: string | number;
  expected_arrival: string;
};

type DemoDataset = {
  Products: ProductRecord[];
  Sales: SaleRecord[];
  Inventory: InventoryRecord[];
  Shipments: ShipmentRecord[];
};

const dataset = demoData as DemoDataset;
const productById = new Map(dataset.Products.map((product) => [product.product_id, product]));

const presentationDefaults = {
  businessName: "Coffee Corner",
  summary:
    "Demand is steady across your core coffee staples, with limited risk in cold brew and pastry inventory. A few mid-week reorder actions will keep service levels strong and prevent stockouts during peak hours.",
  lastUpdated: "8:45 AM",
  kpis: [
    {
      icon: "alert",
      tone: "danger",
      value: "14",
      label: "Need Attention",
      hint: "Products needing action",
      badge: "High priority",
    },
    {
      icon: "check",
      tone: "success",
      value: "118",
      label: "Healthy",
      hint: "Items in good shape",
      badge: "Stable",
    },
    {
      icon: "coins",
      tone: "brand",
      value: "$24,680",
      label: "Total Inventory Value",
      hint: "Across all SKUs",
      badge: "Updated today",
    },
  ] as MockKpi[],
  recentActivity: [
    { title: "Cold Brew order received", detail: "+240 cans", time: "15 min ago", tone: "success" },
    { title: "Blueberry Muffins trending up", detail: "+18% vs last week", time: "1 hour ago", tone: "brand" },
    { title: "Oat milk stock declining", detail: "Only 11 units left", time: "2 hours ago", tone: "warning" },
    { title: "Milk carton restock approved", detail: "2 deliveries scheduled", time: "Today", tone: "neutral" },
  ] as MockDashboardViewModel["recentActivity"],
  stockStatus: [
    { label: "Healthy", value: 68, count: 84, tone: "success" },
    { label: "Low stock", value: 22, count: 26, tone: "danger" },
    { label: "Excess", value: 10, count: 12, tone: "warning" },
  ] as MockDashboardViewModel["stockStatus"],
  quickActions: [
    { label: "Create purchase order", icon: "refresh", variant: "primary" },
    { label: "Review low-stock items", icon: "alert", variant: "secondary" },
    { label: "Export inventory report", icon: "arrow-right", variant: "ghost" },
  ] as Array<{
    label: string;
    icon: "refresh" | "alert" | "arrow-right";
    variant: MockQuickActionVariant;
  }>,
} as const;

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function buildTrendFromSales(): number[] {
  const totalsByDate = new Map<string, number>();

  for (const sale of dataset.Sales) {
    const value = Number(sale.quantity_sold ?? 0);
    totalsByDate.set(sale.date, (totalsByDate.get(sale.date) ?? 0) + value);
  }

  const orderedDates = Array.from(totalsByDate.keys()).sort();
  const trend = orderedDates.slice(-12).map((date) => totalsByDate.get(date) ?? 0);

  if (trend.length < 12) {
    const padded = [...trend];
    while (padded.length < 12) {
      padded.unshift(0);
    }
    return padded;
  }

  return trend;
}

function buildPriorities(): MockDashboardViewModel["priorities"] {
  const inventoryByProduct = new Map<string, number>();

  for (const item of dataset.Inventory) {
    inventoryByProduct.set(item.product_id, Number(item.quantity_on_hand ?? 0));
  }

  return dataset.Products.filter((product) => inventoryByProduct.has(product.product_id))
    .map((product) => {
      const currentStock = inventoryByProduct.get(product.product_id) ?? 0;
      const targetStockDays = Number(product.target_stock_days ?? 0);

      return {
        product_id: product.product_id,
        product_name: product.product_name,
        category: product.category ?? "General",
        current_stock: currentStock,
        days_remaining: Number.isFinite(targetStockDays) ? targetStockDays : 0,
        status: "UNAVAILABLE" as MockPriorityStatus,
      };
    })
    .sort((left, right) => left.current_stock - right.current_stock)
    .slice(0, 4);
}

function buildShipments(): MockDashboardViewModel["shipments"] {
  return dataset.Shipments.map((shipment) => {
    const product = productById.get(shipment.product_id);

    return {
      product: product?.product_name ?? shipment.product_id,
      eta: new Date(`${shipment.expected_arrival}T12:00:00`).toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      }),
      qty: `${Number(shipment.quantity ?? 0)} units`,
      status: "Scheduled",
      tone: "brand",
    };
  });
}

export function buildDashboardViewModel(): MockDashboardViewModel {
  const inventoryByProduct = new Map<string, number>();
  for (const snapshot of dataset.Inventory) {
    inventoryByProduct.set(snapshot.product_id, Number(snapshot.quantity_on_hand ?? 0));
  }

  const totalInventoryValue = dataset.Products.reduce((total, product) => {
    const unitCost = Number(product.unit_cost ?? 0);
    const quantity = inventoryByProduct.get(product.product_id) ?? 0;
    return total + unitCost * quantity;
  }, 0);

  const kpis: MockKpi[] = [
    ...presentationDefaults.kpis.slice(0, 2),
    {
      ...presentationDefaults.kpis[2],
      value: formatCurrency(totalInventoryValue),
    },
  ];

  return {
    businessName: presentationDefaults.businessName,
    summary: presentationDefaults.summary,
    lastUpdated: presentationDefaults.lastUpdated,
    kpis,
    priorities: buildPriorities(),
    recentActivity: presentationDefaults.recentActivity,
    trend: buildTrendFromSales(),
    stockStatus: presentationDefaults.stockStatus,
    shipments: buildShipments(),
    quickActions: presentationDefaults.quickActions,
  };
}
