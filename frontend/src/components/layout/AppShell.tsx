import { useState, type ReactNode } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Bell, ChevronDown, LogOut, RefreshCw, UserCog } from "lucide-react";
import { cn } from "@/lib/utils";
import { alertsQuery, freshnessQuery } from "@/services/queries";
import { navItems } from "./nav";
import { GlobalSearch } from "./GlobalSearch";
import { relativeTime } from "@/lib/format";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function Logo({ compact }: { compact?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-2.5 overflow-hidden">
      <span className="grid size-7 shrink-0 place-items-center rounded-md border border-primary/50 bg-primary/12">
        <span className="text-[13px] font-bold text-primary">S</span>
      </span>
      {!compact && (
        <span className="flex flex-col leading-none">
          <span className="text-sm font-semibold tracking-tight text-foreground">ScoutLab</span>
          <span className="text-[10px] tracking-wider text-muted-foreground uppercase">
            Sorare Intelligence
          </span>
        </span>
      )}
    </Link>
  );
}

function FreshnessIndicator() {
  const { data } = useQuery(freshnessQuery);
  return (
    <div className="hidden items-center gap-2 rounded-md border border-border bg-elevated px-2.5 py-1.5 md:flex">
      <span className="relative flex size-1.5">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-positive/60" />
        <span className="relative inline-flex size-1.5 rounded-full bg-positive" />
      </span>
      <span className="text-[11px] text-muted-foreground">
        {data ? `Updated ${relativeTime(data.lastUpdated)}` : "Syncing…"}
      </span>
    </div>
  );
}

function SidebarNav({ collapsed }: { collapsed: boolean }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const groups: { id: string; label: string }[] = [
    { id: "intelligence", label: "Intelligence" },
    { id: "portfolio", label: "Portfolio" },
    { id: "account", label: "Account" },
  ];

  return (
    <nav className="flex flex-1 flex-col gap-5 overflow-y-auto px-2 py-3">
      {groups.map((g) => (
        <div key={g.id}>
          {!collapsed && <p className="label-caps px-2 pb-1.5">{g.label}</p>}
          <ul className="space-y-0.5">
            {navItems
              .filter((i) => i.group === g.id)
              .map((item) => {
                const active =
                  item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
                return (
                  <li key={item.to}>
                    <Link
                      to={item.to}
                      title={item.label}
                      className={cn(
                        "group flex items-center gap-2.5 rounded-md px-2 py-1.5 text-[13px] font-medium transition-colors",
                        active
                          ? "bg-sidebar-accent text-foreground"
                          : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground",
                        collapsed && "justify-center",
                      )}
                    >
                      <span
                        className={cn(
                          "-ml-2 h-4 w-0.5 rounded-full",
                          active ? "bg-primary" : "bg-transparent",
                          collapsed && "hidden",
                        )}
                      />
                      <item.icon
                        className={cn("size-4 shrink-0", active && "text-primary")}
                      />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                    </Link>
                  </li>
                );
              })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

function MobileNav() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-sidebar/95 backdrop-blur md:hidden">
      <ul className="grid grid-cols-5">
        {navItems
          .filter((i) => i.mobile)
          .map((item) => {
            const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  className={cn(
                    "flex flex-col items-center gap-1 py-2 text-[10px] font-medium transition-colors",
                    active ? "text-primary" : "text-muted-foreground",
                  )}
                >
                  <item.icon className="size-4" />
                  {item.label}
                </Link>
              </li>
            );
          })}
      </ul>
    </nav>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const { data: alerts } = useQuery(alertsQuery);
  const unread = alerts?.filter((a) => !a.read).length ?? 0;

  return (
    <div className="min-h-screen bg-background">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-30 hidden flex-col border-r border-sidebar-border bg-sidebar md:flex",
          collapsed ? "w-[60px]" : "w-[172px] lg:w-[212px]",
        )}
      >
        <div
          className={cn(
            "flex h-14 items-center border-b border-sidebar-border px-3",
            collapsed && "justify-center px-0",
          )}
        >
          <Logo compact={collapsed} />
        </div>
        <SidebarNav collapsed={collapsed} />
        <button
          type="button"
          onClick={() => setCollapsed((v) => !v)}
          className="mx-2 mb-3 rounded-md border border-sidebar-border px-2 py-1.5 text-[11px] text-muted-foreground transition-colors hover:text-foreground"
        >
          {collapsed ? "›" : "‹ Collapse"}
        </button>
      </aside>

      <div className={cn("flex min-h-screen flex-col", collapsed ? "md:pl-[60px]" : "md:pl-[172px] lg:pl-[212px]")}>
        <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-border bg-background/90 px-3 backdrop-blur md:px-5">
          <div className="md:hidden">
            <Logo compact />
          </div>
          <div className="flex-1">
            <GlobalSearch />
          </div>
          <FreshnessIndicator />
          <Link
            to="/alerts"
            className="relative grid size-8 place-items-center rounded-md border border-border bg-elevated text-muted-foreground transition-colors hover:text-foreground"
            aria-label={`Alerts${unread ? `, ${unread} unread` : ""}`}
          >
            <Bell className="size-4" />
            {unread > 0 && (
              <span className="tabular absolute -top-1.5 -right-1.5 grid min-w-4 place-items-center rounded-full bg-negative px-1 text-[10px] font-semibold text-negative-foreground">
                {unread}
              </span>
            )}
          </Link>
          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-md border border-border bg-elevated py-1 pr-1.5 pl-1 transition-colors hover:border-border-strong">
              <span className="grid size-6 place-items-center rounded bg-primary/15 text-[11px] font-semibold text-primary">
                SM
              </span>
              <span className="hidden text-xs font-medium text-foreground sm:block">simon</span>
              <ChevronDown className="size-3.5 text-muted-foreground" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52">
              <DropdownMenuLabel className="text-xs">
                simon
                <span className="block text-[11px] font-normal text-muted-foreground">
                  ScoutLab private group
                </span>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild className="text-xs">
                <Link to="/settings">
                  <UserCog className="size-3.5" /> Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem className="text-xs">
                <RefreshCw className="size-3.5" /> Force data refresh
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-xs text-negative">
                <LogOut className="size-3.5" /> Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        <main className="flex-1 px-3 pt-4 pb-20 md:px-5 md:pb-8">{children}</main>
      </div>

      <MobileNav />
    </div>
  );
}

export function PageHeader({
  title,
  description,
  actions,
  meta,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  meta?: ReactNode;
}) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-foreground">{title}</h1>
        {description && <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>}
        {meta && <div className="mt-2 flex flex-wrap items-center gap-2">{meta}</div>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}
