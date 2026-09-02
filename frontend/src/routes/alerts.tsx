import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BellRing, CheckCheck } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/layout/AppShell";
import {
  CategoryTag,
  EmptyState,
  ErrorState,
  Panel,
  Tag,
} from "@/components/scoutlab/primitives";
import { Button } from "@/components/ui/button";
import { api } from "@/services/api";
import { alertsQuery, qk } from "@/services/queries";
import { relativeTime } from "@/lib/format";
import type { AlertCategory } from "@/types";

const categories: (AlertCategory | "All")[] = [
  "All",
  "Injury",
  "Suspension",
  "Price",
  "Starting XI",
  "Fixture",
  "Performance",
];

export const Route = createFileRoute("/alerts")({
  head: () => ({
    meta: [
      { title: "Alerts — Signal Centre | ScoutLab" },
      {
        name: "description",
        content:
          "ScoutLab alert centre: injury, suspension, price, starting XI, fixture and performance signals with read and unread states.",
      },
      { property: "og:title", content: "Alerts — Signal Centre | ScoutLab" },
      {
        property: "og:description",
        content: "Every ScoutLab signal in one place, grouped by category and freshness.",
      },
    ],
  }),
  component: AlertsPage,
});

function AlertsPage() {
  const qc = useQueryClient();
  const [category, setCategory] = useState<(typeof categories)[number]>("All");
  const [onlyUnread, setOnlyUnread] = useState(false);
  const alerts = useQuery(alertsQuery);

  const markRead = useMutation({
    mutationFn: (id: string) => api.markAlertRead(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: qk.alerts }),
  });
  const markAll = useMutation({
    mutationFn: () => api.markAllAlertsRead(),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: qk.alerts });
      toast.success("All alerts marked as read");
    },
  });

  const rows = (alerts.data ?? []).filter(
    (a) => (category === "All" || a.category === category) && (!onlyUnread || !a.read),
  );
  const unread = (alerts.data ?? []).filter((a) => !a.read).length;

  return (
    <>
      <PageHeader
        title="Alerts"
        description={`${unread} unread signal${unread === 1 ? "" : "s"}`}
        meta={
          <div className="flex flex-wrap gap-1.5">
            {categories.map((c) => (
              <button key={c} type="button" onClick={() => setCategory(c)}>
                <Tag tone={category === c ? "primary" : "muted"} className="normal-case tracking-normal">
                  {c}
                </Tag>
              </button>
            ))}
          </div>
        }
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs"
              onClick={() => setOnlyUnread((v) => !v)}
            >
              {onlyUnread ? "Showing unread" : "Show all"}
            </Button>
            <Button
              size="sm"
              className="h-8 gap-1.5 text-xs"
              onClick={() => markAll.mutate()}
              disabled={unread === 0}
            >
              <CheckCheck className="size-3.5" /> Mark all read
            </Button>
          </>
        }
      />

      <Panel>
        {alerts.isError ? (
          <ErrorState onRetry={() => void alerts.refetch()} />
        ) : rows.length === 0 ? (
          <EmptyState
            icon={BellRing}
            title="Nothing to review"
            description="No alerts match this filter. New signals arrive as availability, prices and line-ups change."
          />
        ) : (
          <ul className="divide-y divide-border">
            {rows.map((a) => (
              <li
                key={a.id}
                className={
                  a.read
                    ? "flex gap-3 px-4 py-3"
                    : "flex gap-3 border-l-2 border-l-primary bg-primary/5 px-4 py-3"
                }
              >
                <span
                  className={
                    a.severity === "positive"
                      ? "mt-1.5 size-1.5 shrink-0 rounded-full bg-positive"
                      : a.severity === "warning"
                        ? "mt-1.5 size-1.5 shrink-0 rounded-full bg-warning"
                        : a.severity === "negative"
                          ? "mt-1.5 size-1.5 shrink-0 rounded-full bg-negative"
                          : "mt-1.5 size-1.5 shrink-0 rounded-full bg-primary"
                  }
                />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <CategoryTag value={a.category} />
                    {!a.read && <Tag tone="primary">New</Tag>}
                    <span className="tabular ml-auto text-[10px] text-muted-foreground">
                      {relativeTime(a.createdAt)}
                    </span>
                  </div>
                  <p className="mt-1.5 text-sm font-medium text-foreground">{a.title}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{a.detail}</p>
                  <div className="mt-2 flex items-center gap-3">
                    {a.playerId && (
                      <Link
                        to="/players/$playerId"
                        params={{ playerId: a.playerId }}
                        className="text-[11px] text-primary hover:underline"
                      >
                        Open profile
                      </Link>
                    )}
                    {!a.read && (
                      <button
                        type="button"
                        onClick={() => markRead.mutate(a.id)}
                        className="text-[11px] text-muted-foreground hover:text-foreground"
                      >
                        Mark read
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </>
  );
}
