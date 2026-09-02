import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/layout/AppShell";
import { DataTable, type Column } from "@/components/scoutlab/DataTable";
import {
  AvailabilityBadge,
  Delta,
  KpiCard,
  KpiSkeleton,
  Panel,
  RarityTag,
  ScoutScore,
} from "@/components/scoutlab/primitives";
import { PlayerIdentity, PositionTag, initials } from "@/components/scoutlab/PlayerIdentity";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cardsQuery, portfolioQuery } from "@/services/queries";
import { eth } from "@/lib/format";
import type { Card } from "@/types";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/my-cards")({
  head: () => ({
    meta: [
      { title: "My Cards — Portfolio Performance | ScoutLab" },
      {
        name: "description",
        content:
          "Track your Sorare card portfolio: total value, change since acquisition, average score, best performers and cards at risk.",
      },
      { property: "og:title", content: "My Cards — Portfolio Performance | ScoutLab" },
      {
        property: "og:description",
        content: "Portfolio valuation, scoring output and risk view for every card you hold.",
      },
    ],
  }),
  component: MyCardsPage,
});

function VisualCard({ card, onClick }: { card: Card; onClick: () => void }) {
  const p = card.player;
  const rarityColors = {
    common: "from-slate-200 to-slate-400 text-slate-900 border-slate-300",
    limited: "from-amber-200 to-yellow-500 text-amber-950 border-amber-300",
    rare: "from-red-500 to-red-700 text-white border-red-600",
    "super rare": "from-blue-500 to-blue-800 text-white border-blue-600",
    unique: "from-neutral-800 to-black text-white border-neutral-700",
  };
  const color = rarityColors[card.rarity] || rarityColors.common;

  return (
    <div
      onClick={onClick}
      className={cn(
        "relative cursor-pointer overflow-hidden rounded-xl border bg-gradient-to-br transition-all hover:scale-105 hover:shadow-xl shadow-md",
        color
      )}
      style={{ aspectRatio: "2/3" }}
    >
      <div className="absolute inset-x-0 top-0 p-3 flex justify-between items-start z-10 drop-shadow-md">
        <div className="font-black text-xl tracking-tighter">{p.projectedScore.toFixed(0)}</div>
        <div className="text-[10px] font-bold uppercase tracking-widest opacity-80">{card.season}</div>
      </div>
      
      {p.photoUrl ? (
        <img src={p.photoUrl} alt={p.name} className="absolute inset-0 h-full w-full object-cover object-top mix-blend-luminosity opacity-80" />
      ) : (
        <div className="absolute inset-0 flex items-center justify-center opacity-20 text-7xl font-black tracking-tighter">
          {initials(p.name)}
        </div>
      )}

      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-3 pt-12 text-white">
        <h3 className="font-bold text-sm leading-tight truncate drop-shadow-md">{p.name}</h3>
        <p className="text-[10px] opacity-90 truncate font-medium">{p.club}</p>
        <div className="mt-2 flex justify-between items-center text-[9px] font-bold uppercase tracking-widest opacity-80">
          <span>{p.position}</span>
          <span>#{card.serial}</span>
        </div>
      </div>
    </div>
  );
}

function MyCardsPage() {
  const navigate = useNavigate();
  const cards = useQuery(cardsQuery);
  const portfolio = useQuery(portfolioQuery);

  const rows = cards.data ?? [];
  const best = [...rows].sort((a, b) => b.player.form - a.player.form).slice(0, 4);
  const atRisk = rows.filter(
    (c) => c.player.availability !== "AVAILABLE" || c.player.risk === "HIGH",
  );

  const columns: Column<Card>[] = [
    { key: "player", header: "Player", width: "210px", render: (c) => <PlayerIdentity player={c.player} /> },
    { key: "pos", header: "Pos", render: (c) => <PositionTag value={c.player.position} /> },
    { key: "rarity", header: "Rarity", render: (c) => <RarityTag value={c.rarity} /> },
    {
      key: "serial",
      header: "Card",
      hideBelow: "lg",
      render: (c) => <span className="tabular text-xs text-muted-foreground">#{c.serial}</span>,
    },
    {
      key: "season",
      header: "Season",
      hideBelow: "md",
      render: (c) => <span className="text-xs text-muted-foreground">{c.season}</span>,
    },
    {
      key: "price",
      header: "Price",
      align: "right",
      render: (c) => <span className="tabular text-xs">{eth(c.price)}</span>,
    },
    {
      key: "pnl",
      header: "P/L",
      align: "right",
      render: (c) => <Delta value={((c.price - c.acquiredPrice) / c.acquiredPrice) * 100} />,
    },
    {
      key: "avg",
      header: "Avg",
      align: "right",
      hideBelow: "sm",
      render: (c) => <span className="tabular text-xs">{c.player.averageScore.toFixed(1)}</span>,
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
      hideBelow: "lg",
      render: (c) => <ScoutScore value={Math.round(c.player.form)} />,
    },
    {
      key: "fixture",
      header: "Fixture",
      hideBelow: "xl",
      render: (c) => (
        <span className="text-xs text-muted-foreground">
          vs {c.player.scores.at(-1)?.opponent ?? "—"}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (c) => <AvailabilityBadge value={c.player.availability} />,
    },
  ];

  return (
    <>
      <PageHeader title="My Cards" description="Personal portfolio valuation and performance" />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        {portfolio.isLoading || !portfolio.data ? (
          <KpiSkeleton count={5} />
        ) : (
          <>
            <KpiCard
              label="Total card value"
              value={eth(portfolio.data.totalValue)}
              delta={portfolio.data.changePct7d}
            />
            <KpiCard
              label="Unrealised P/L"
              value={eth(portfolio.data.change7d)}
              tone={portfolio.data.change7d >= 0 ? "positive" : "negative"}
            />
            <KpiCard label="Average score" value={portfolio.data.averageScore.toFixed(0)} />
            <KpiCard label="Cards held" value={String(portfolio.data.cardCount)} />
            <KpiCard
              label="Cards at risk"
              value={String(atRisk.length)}
              tone="negative"
              hint="Unavailable or high variance"
            />
          </>
        )}
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_320px]">
        <Panel title="Portfolio" subtitle="All cards with valuation and projected output">
          <Tabs defaultValue="gallery" className="flex flex-col">
            <div className="border-b border-border px-4 py-2">
              <TabsList className="h-8 bg-elevated">
                <TabsTrigger value="gallery" className="text-xs">Gallery</TabsTrigger>
                <TabsTrigger value="table" className="text-xs">Table</TabsTrigger>
              </TabsList>
            </div>
            <TabsContent value="gallery" className="p-4 m-0">
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {rows.map((c) => (
                  <VisualCard 
                    key={c.id} 
                    card={c} 
                    onClick={() => navigate({ to: "/players/$playerId", params: { playerId: c.playerId } })}
                  />
                ))}
              </div>
            </TabsContent>
            <TabsContent value="table" className="m-0">
              <DataTable
                columns={columns}
                rows={rows}
                rowKey={(c) => c.id}
                isLoading={cards.isLoading}
                onRowClick={(c) =>
                  void navigate({ to: "/players/$playerId", params: { playerId: c.playerId } })
                }
              />
            </TabsContent>
          </Tabs>
        </Panel>

        <div className="space-y-4">
          <Panel title="Best performing" subtitle="Ranked by current form">
            <ul className="divide-y divide-border">
              {best.map((c) => (
                <li key={c.id} className="flex items-center gap-2 px-4 py-2.5">
                  <PlayerIdentity player={c.player} />
                  <span className="tabular ml-auto text-xs text-positive">
                    {c.player.form.toFixed(1)}
                  </span>
                </li>
              ))}
            </ul>
          </Panel>
          <Panel title="Cards at risk" subtitle="Availability or variance concerns">
            {atRisk.length === 0 ? (
              <p className="px-4 py-6 text-center text-xs text-muted-foreground">
                No risk flags on your portfolio.
              </p>
            ) : (
              <ul className="divide-y divide-border">
                {atRisk.map((c) => (
                  <li key={c.id} className="px-4 py-2.5">
                    <PlayerIdentity player={c.player} />
                    <div className="mt-1.5">
                      <AvailabilityBadge value={c.player.availability} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        </div>
      </div>
    </>
  );
}
