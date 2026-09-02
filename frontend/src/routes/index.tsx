import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, RefreshCw } from "lucide-react";
import { PageHeader } from "@/components/layout/AppShell";
import { DataTable, type Column } from "@/components/scoutlab/DataTable";
import {
  AvailabilityBadge,
  Delta,
  ErrorState,
  KpiCard,
  KpiSkeleton,
  Panel,
  RecommendationBadge,
  ScoutScore,
  Tag,
} from "@/components/scoutlab/primitives";
import { PlayerIdentity, PositionTag } from "@/components/scoutlab/PlayerIdentity";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  alertsQuery,
  cardsQuery,
  freshnessQuery,
  kpisQuery,
  marketQuery,
  opportunitiesQuery,
} from "@/services/queries";
import { eth, relativeTime } from "@/lib/format";
import type { Card, Player } from "@/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ScoutLab — Sorare Scouting & Market Intelligence" },
      {
        name: "description",
        content:
          "ScoutLab is a private Sorare intelligence terminal: scout scores, form models, starting XI probability and live market signals in one dark analytics workspace.",
      },
      { property: "og:title", content: "ScoutLab — Sorare Scouting & Market Intelligence" },
      {
        property: "og:description",
        content:
          "Scouting opportunities, squad risk, fixture difficulty and market movers for a private group of Sorare managers.",
      },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const navigate = useNavigate();
  const freshness = useQuery(freshnessQuery);
  const kpis = useQuery(kpisQuery);
  const opportunities = useQuery(opportunitiesQuery);
  const cards = useQuery(cardsQuery);
  const alerts = useQuery(alertsQuery);
  const market = useQuery(marketQuery);

  const oppColumns: Column<Player>[] = [
    { key: "player", header: "Player", width: "210px", render: (p) => <PlayerIdentity player={p} /> },
    { key: "pos", header: "Pos", render: (p) => <PositionTag value={p.position} /> },
    {
      key: "age",
      header: "Age",
      align: "right",
      hideBelow: "md",
      render: (p) => <span className="tabular text-xs">{p.age}</span>,
    },
    {
      key: "avg",
      header: "Avg",
      align: "right",
      render: (p) => <span className="tabular text-xs">{p.averageScore.toFixed(1)}</span>,
    },
    {
      key: "form",
      header: "Form",
      align: "right",
      hideBelow: "sm",
      render: (p) => (
        <span
          className={
            p.form >= p.averageScore ? "tabular text-xs text-positive" : "tabular text-xs text-negative"
          }
        >
          {p.form.toFixed(1)}
        </span>
      ),
    },
    {
      key: "proj",
      header: "Proj",
      align: "right",
      hideBelow: "md",
      render: (p) => <span className="tabular text-xs">{p.projectedScore.toFixed(1)}</span>,
    },
    {
      key: "startxi",
      header: "Start XI",
      hideBelow: "lg",
      render: (p) => <ScoutScore value={p.startingProbability} />,
    },
    {
      key: "price",
      header: "Price",
      align: "right",
      render: (p) => <span className="tabular text-xs">{eth(p.marketPrice)}</span>,
    },
    { key: "scout", header: "Scout", render: (p) => <ScoutScore value={p.scoutScore} /> },
    { key: "rec", header: "Call", render: (p) => <RecommendationBadge value={p.recommendation} /> },
  ];

  const squadColumns: Column<Card>[] = [
    { key: "player", header: "Player", width: "210px", render: (c) => <PlayerIdentity player={c.player} /> },
    { key: "pos", header: "Pos", render: (c) => <PositionTag value={c.player.position} /> },
    {
      key: "next",
      header: "Next",
      hideBelow: "md",
      render: (c) => <span className="text-xs text-muted-foreground">{c.player.scores.at(-1)?.opponent ?? "—"}</span>,
    },
    {
      key: "proj",
      header: "Proj",
      align: "right",
      render: (c) => <span className="tabular text-xs">{c.player.projectedScore.toFixed(1)}</span>,
    },
    {
      key: "form",
      header: "Form",
      align: "right",
      hideBelow: "sm",
      render: (c) => <span className="tabular text-xs">{c.player.form.toFixed(1)}</span>,
    },
    {
      key: "avail",
      header: "Availability",
      hideBelow: "lg",
      render: (c) => <AvailabilityBadge value={c.player.availability} />,
    },
    {
      key: "value",
      header: "Value",
      align: "right",
      render: (c) => <span className="tabular text-xs">{eth(c.price)}</span>,
    },
  ];

  const moverColumns = (): Column<Player>[] => [
    { key: "player", header: "Player", render: (p) => <PlayerIdentity player={p} /> },
    {
      key: "price",
      header: "Price",
      align: "right",
      render: (p) => <span className="tabular text-xs">{eth(p.marketPrice)}</span>,
    },
    { key: "d7", header: "7d", align: "right", render: (p) => <Delta value={p.priceChange7d} /> },
    { key: "scout", header: "Scout", hideBelow: "sm", render: (p) => <ScoutScore value={p.scoutScore} /> },
  ];

  return (
    <>
      <PageHeader
        title="ScoutLab"
        description="Private Sorare scouting and market intelligence terminal"
        meta={
          <>
            <Tag tone="primary">{freshness.data?.gameweek.label ?? "GW —"} live</Tag>
            <Tag tone="positive">
              {freshness.data ? `Updated ${relativeTime(freshness.data.lastUpdated)}` : "Syncing"}
            </Tag>
            <span className="text-[11px] text-muted-foreground">
              Sources: club statements, fixture models, Sorare market feed
            </span>
          </>
        }
        actions={
          <Button
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-xs"
            onClick={() => void freshness.refetch()}
          >
            <RefreshCw className={freshness.isFetching ? "size-3.5 animate-spin" : "size-3.5"} />
            Refresh data
          </Button>
        }
      />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        {kpis.isLoading || !kpis.data ? (
          <KpiSkeleton />
        ) : (
          <>
            <KpiCard
              label="Squad Value"
              value={eth(kpis.data.squadValue)}
              delta={kpis.data.squadValueChange}
              hint="14 cards across 5 competitions"
            />
            <KpiCard
              label="Squad Avg Score"
              value={kpis.data.squadAverageScore.toFixed(0)}
              delta={kpis.data.squadAverageScoreChange}
              hint="Rolling 5 gameweeks"
            />
            <KpiCard
              label="Players In Form"
              value={String(kpis.data.playersInForm)}
              tone="positive"
              hint="Form above season average"
            />
            <KpiCard
              label="Players At Risk"
              value={String(kpis.data.playersAtRisk)}
              tone="negative"
              hint="Injury, suspension or high variance"
            />
            <KpiCard
              label="Market Opportunities"
              value={String(kpis.data.marketOpportunities)}
              tone="warning"
              hint="BUY calls in the current model"
            />
            <KpiCard
              label="Upcoming Fixtures"
              value={String(kpis.data.upcomingFixtures)}
              hint={`${freshness.data?.gameweek.label ?? "GW"} window`}
            />
          </>
        )}
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_320px]">
        <div className="min-w-0 space-y-4">
          <Panel
            title="Scouting Opportunities"
            subtitle="Highest Scout Score among available players"
            actions={
              <Link
                to="/scout"
                className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
              >
                Open Scout <ArrowUpRight className="size-3" />
              </Link>
            }
          >
            {opportunities.isError ? (
              <ErrorState onRetry={() => void opportunities.refetch()} />
            ) : (
              <DataTable
                columns={oppColumns}
                rows={opportunities.data ?? []}
                rowKey={(p) => p.id}
                isLoading={opportunities.isLoading}
                onRowClick={(p) =>
                  void navigate({ to: "/players/$playerId", params: { playerId: p.id } })
                }
              />
            )}
          </Panel>

          <Panel
            title="Squad Overview"
            subtitle="Your cards, next fixture and projected output"
            actions={
              <Link
                to="/my-cards"
                className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
              >
                Portfolio <ArrowUpRight className="size-3" />
              </Link>
            }
          >
            <DataTable
              columns={squadColumns}
              rows={(cards.data ?? []).slice(0, 8)}
              rowKey={(c) => c.id}
              isLoading={cards.isLoading}
              onRowClick={(c) =>
                void navigate({ to: "/players/$playerId", params: { playerId: c.playerId } })
              }
            />
          </Panel>

          <Panel title="Market Intelligence" subtitle="Movement across the tracked universe">
            <Tabs defaultValue="risers" className="p-3">
              <TabsList className="h-8 bg-elevated">
                <TabsTrigger value="risers" className="text-xs">
                  Risers
                </TabsTrigger>
                <TabsTrigger value="fallers" className="text-xs">
                  Fallers
                </TabsTrigger>
                <TabsTrigger value="undervalued" className="text-xs">
                  Undervalued
                </TabsTrigger>
                <TabsTrigger value="volume" className="text-xs">
                  High volume
                </TabsTrigger>
              </TabsList>
              {(
                [
                  ["risers", market.data?.risers],
                  ["fallers", market.data?.fallers],
                  ["undervalued", market.data?.undervalued],
                  ["volume", market.data?.highVolume],
                ] as const
              ).map(([key, rows]) => (
                <TabsContent key={key} value={key} className="mt-3">
                  <DataTable
                    columns={moverColumns()}
                    rows={(rows ?? []).slice(0, 6)}
                    rowKey={(p) => p.id}
                    isLoading={market.isLoading}
                    dense
                    onRowClick={(p) =>
                      void navigate({ to: "/players/$playerId", params: { playerId: p.id } })
                    }
                  />
                </TabsContent>
              ))}
            </Tabs>
          </Panel>
        </div>

        <Panel
          title="Alerts"
          subtitle="Latest signals for your squad and watchlist"
          actions={
            <Link to="/alerts" className="text-[11px] font-medium text-primary hover:underline">
              All
            </Link>
          }
        >
          <ul className="divide-y divide-border">
            {(alerts.data ?? []).slice(0, 9).map((a) => (
              <li key={a.id} className="px-4 py-2.5">
                <div className="flex items-center gap-2">
                  <span
                    className={
                      a.severity === "positive"
                        ? "size-1.5 rounded-full bg-positive"
                        : a.severity === "warning"
                          ? "size-1.5 rounded-full bg-warning"
                          : a.severity === "negative"
                            ? "size-1.5 rounded-full bg-negative"
                            : "size-1.5 rounded-full bg-primary"
                    }
                  />
                  <span className="label-caps">{a.category}</span>
                  <span className="tabular ml-auto text-[10px] text-muted-foreground">
                    {relativeTime(a.createdAt)}
                  </span>
                </div>
                <p className="mt-1 text-xs font-medium text-foreground">{a.title}</p>
                <p className="mt-0.5 text-[11px] text-muted-foreground">{a.detail}</p>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </>
  );
}
