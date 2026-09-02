import {
  Activity,
  BellRing,
  Binoculars,
  CalendarDays,
  LayoutDashboard,
  LineChart,
  Newspaper,
  Settings,
  Star,
  Users,
  Wallet,
} from "lucide-react";

export interface NavItem {
  label: string;
  to: string;
  icon: typeof Activity;
  group: "intelligence" | "portfolio" | "account";
  mobile?: boolean;
}

export const navItems: NavItem[] = [
  { label: "Dashboard", to: "/", icon: LayoutDashboard, group: "intelligence", mobile: true },
  { label: "Scout", to: "/scout", icon: Binoculars, group: "intelligence", mobile: true },
  { label: "Players", to: "/players", icon: Users, group: "intelligence" },
  { label: "Market", to: "/market", icon: LineChart, group: "intelligence", mobile: true },
  { label: "Fixtures", to: "/fixtures", icon: CalendarDays, group: "intelligence" },
  { label: "My Cards", to: "/my-cards", icon: Wallet, group: "portfolio", mobile: true },
  { label: "Watchlist", to: "/watchlist", icon: Star, group: "portfolio" },
  { label: "News", to: "/news", icon: Newspaper, group: "intelligence" },
  { label: "Group", to: "/group", icon: Activity, group: "portfolio" },
  { label: "Alerts", to: "/alerts", icon: BellRing, group: "account", mobile: true },
  { label: "Settings", to: "/settings", icon: Settings, group: "account" },
];
