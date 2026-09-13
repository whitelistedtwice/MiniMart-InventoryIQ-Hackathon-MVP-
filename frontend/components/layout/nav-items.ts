import type { IconName } from "@/components/ui/icons";

/*
  The only approved top-level navigation for the MVP.
  Do not add Customers, Orders, Suppliers, Reports, Billing, Team, etc.
*/

export type NavItem = {
  href: string;
  label: string;
  icon: IconName;
};

export const NAV_ITEMS: readonly NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: "dashboard" },
  { href: "/inventory", label: "Inventory", icon: "inventory" },
  { href: "/analytics", label: "Analytics", icon: "analytics" },
  { href: "/settings", label: "Settings", icon: "settings" },
];
