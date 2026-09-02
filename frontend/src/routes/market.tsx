import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/layout/AppShell";
import { DataTable, type Column } from "@/components/scoutlab/DataTable";
import {
  Delta,
  ErrorState,
  KpiCard,
  KpiSkeleton,
  Panel,
  RarityTag,
  RecommendationBadge,
  ScoutScore,
} from "@/components/scoutlab/primitives";
import { AreaTrend } from "@/components/scoutlab/charts";
import { PlayerIdentity } from "@/components/scoutlab/PlayerIdentity";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { marketQuery } from "@/services/queries";
import { eth, relativeTime, shortDate } from "@/lib/format";
import type { Player } from "@/types";

export const Route = createFileRoute("/market")({
  head: () => ({
    meta: [
      { title: "Market Intelligence — Prices & Movers | ScoutLab" },
      {
        name: "description",
        content:
          "Sorare market overview: price index, biggest risers and fallers, undervalued players, trading volume and recent sales.",
      },
      { property: "og:title", content: "Market Intelligence — Prices & Movers | ScoutLab" },
      {
        property: "og:description",
        content: "Track the ScoutLab price index, movers, undervalued targets and recent sales.",
      },
    ],
  }),
  component: MarketPage,
});

function MarketPage() {
  const navigate = useNavigate();
  const market = useQuery(marketQuery);

  const columns: Column<Player>[] = [
    { key: "player", header: "Player", width: "210px", render: (p) => <PlayerIdentity player={p} /> },
    {
      key: "comp",
      header: "Competition",
      hideBelow: "lg",
      render: (p) => <span className="text-xs text-muted-foreground">{p.competition}</span>,
    },
    {
      key: "price",
      header: "Price",
      align: "right",
      render: (p) => <span className="tabular text-xs">{eth(p.marketPrice)}</span>,
    },
    { key: "d7", header: "7d", align: "right", render: (p) => <Delta value={p.priceChange7d} /> },
    {
      key: "avg",
      header: "Avg score",
      align: "right",
      hideBelow: "sm",
      render: (p) => <span className="tabular text-xs">{p.averageScore.toFixed(1)}</span>,
    },
    { key: "scout", header: "Scout", render: (p) => <ScoutScore value={p.scoutScore} /> },
    { key: "rec", header: "Call", render: (p) => <RecommendationBadge value={p.recommendation} /> },
  ];

  const indexData = (market.data?.indexHistory ?? []).map((h) => ({
    date: shortDate(h.date),
    price: h.price,
  }));

  return (
    <>
      <PageHeader title="Market" description="Price discovery and liquidity across the tracked universe" />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {market.isLoading || !market.data ? (
          <KpiSkeleton count={4} />
        ) : (
          <>
            <KpiCard
              label="7d Volume"
              value={eth(market.data.totalVolume7d, 0)}
              delta={market.data.indexChange7d}
            />
            <KpiCard label="Active listings" value={market.data.activeListings.toLocaleString()} />
            <KpiCard label="Median price" value={eth(market.data.medianPrice)} />
            <KpiCard
              label="ScoutLab index"
              value={indexData.at(-1)?.price.toFixed(1) ?? "—"}
              delta={market.data.indexChange7d}
              tone="positive"
            />
          </>
        )}
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_340px]">
        <div className="min-w-0 space-y-4">
          <Panel
            title="ScoutLab price index"
            subtitle="Equal-weighted basket of tracked players, 60 days"
            bodyClassName="p-3"
          >
            <AreaTrend data={indexData} xKey="date" yKey="price" height={220} />
          </Panel>

          <Panel title="Price movers" subtitle="7-day change across the universe">
            {market.isError ? (
              <ErrorState onRetry={() => void market.refetch()} />
            ) : (
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
                    Trending volume
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
                      columns={columns}
                      rows={rows ?? []}
                      rowKey={(p) => p.id}
                      isLoading={market.isLoading}
                      onRowClick={(p) =>
                        void navigate({ to: "/players/$playerId", params: { playerId: p.id } })
                      }
                    />
                  </TabsContent>
                ))}
              </Tabs>
            )}
          </Panel>
        </div>

        <Panel title="Recent sales" subtitle="Latest confirmed transactions">
          <ul className="divide-y divide-border">
            {(market.data?.recentSales ?? []).map((s) => (
              <li key={s.id} className="flex items-center gap-2 px-4 py-2.5">
                <div className="min-w-0">
                  <p className="truncate text-xs font-medium text-foreground">{s.playerName}</p>
                  <div className="mt-1 flex items-center gap-2">
                    <RarityTag value={s.rarity} />
                    <span className="text-[10px] text-muted-foreground">
                      {relativeTime(s.date)}
                    </span>
                  </div>
                </div>
                <span className="tabular ml-auto text-xs text-foreground">{eth(s.price)}</span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </>
  );
}
