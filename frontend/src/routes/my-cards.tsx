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
import { PlayerIdentity, PositionTag } from "@/components/scoutlab/PlayerIdentity";
import { cardsQuery, portfolioQuery } from "@/services/queries";
import { eth } from "@/lib/format";
import type { Card } from "@/types";

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
          <DataTable
            columns={columns}
            rows={rows}
            rowKey={(c) => c.id}
            isLoading={cards.isLoading}
            onRowClick={(c) =>
              void navigate({ to: "/players/$playerId", params: { playerId: c.playerId } })
            }
          />
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
