import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Star } from "lucide-react";
import { toast } from "sonner";
import {
  AvailabilityBadge,
  ConfidenceTag,
  Delta,
  DifficultyPips,
  ErrorState,
  Panel,
  ProvenanceTag,
  RecommendationBadge,
  RiskBadge,
  ScoreBar,
  ScoutScore,
  Tag,
} from "@/components/scoutlab/primitives";
import { AreaTrend, Bars, MultiLine } from "@/components/scoutlab/charts";
import { DataTable, type Column } from "@/components/scoutlab/DataTable";
import { initials } from "@/components/scoutlab/PlayerIdentity";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/services/api";
import { playerFixturesQuery, playerMarketQuery, playerQuery, qk } from "@/services/queries";
import { dateTime, eth, relativeTime, shortDate } from "@/lib/format";
import type { PlayerFixture } from "@/types";

export const Route = createFileRoute("/players/$playerId")({
  head: () => ({
    meta: [
      { title: "Player Profile — Scouting Report | ScoutLab" },
      {
        name: "description",
        content:
          "Full scouting report: score history, form trend, projected vs actual output, availability, fixtures, market price history and risk factors.",
      },
      { property: "og:title", content: "Player Profile — Scouting Report | ScoutLab" },
      {
        property: "og:description",
        content:
          "ScoutLab scouting report with Scout Score explanation, confidence level and clearly labelled facts, reports and predictions.",
      },
    ],
  }),
  component: PlayerProfile,
});

function Metric({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="border-b border-border px-4 py-2.5 last:border-0 sm:border-r sm:border-b-0 sm:last:border-r-0">
      <p className="label-caps">{label}</p>
      <p className="tabular mt-1 text-lg leading-none font-semibold text-foreground">{value}</p>
      {hint && <p className="mt-1 text-[11px] text-muted-foreground">{hint}</p>}
    </div>
  );
}

function PlayerProfile() {
  const { playerId } = Route.useParams();
  const qc = useQueryClient();
  const player = useQuery(playerQuery(playerId));
  const market = useQuery(playerMarketQuery(playerId));
  const fixtures = useQuery(playerFixturesQuery(playerId));

  const addToWatchlist = useMutation({
    mutationFn: () => api.addToWatchlist(playerId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: qk.watchlist });
      toast.success("Added to watchlist", { description: player.data?.name });
    },
  });

  if (player.isError) return <ErrorState message="This player could not be loaded." />;

  if (player.isLoading || !player.data) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-28 w-full bg-muted" />
        <Skeleton className="h-24 w-full bg-muted" />
        <Skeleton className="h-64 w-full bg-muted" />
      </div>
    );
  }

  const p = player.data;
  const scoreData = p.scores.map((s) => ({
    gw: `GW${s.gameweek}`,
    score: s.score,
    projected: s.projected,
    minutes: s.minutes,
  }));
  const priceData = (market.data?.history ?? []).map((h) => ({
    date: shortDate(h.date),
    price: h.price,
  }));

  const fixtureColumns: Column<PlayerFixture>[] = [
    {
      key: "gw",
      header: "GW",
      render: (f) => <span className="tabular text-xs">{f.fixture.gameweek}</span>,
    },
    { key: "opp", header: "Opponent", render: (f) => <span className="text-xs">{f.opponent}</span> },
    {
      key: "ha",
      header: "H/A",
      render: (f) => <Tag tone={f.isHome ? "primary" : "muted"}>{f.isHome ? "H" : "A"}</Tag>,
    },
    {
      key: "comp",
      header: "Competition",
      hideBelow: "md",
      render: (f) => <span className="text-xs text-muted-foreground">{f.fixture.competition}</span>,
    },
    { key: "diff", header: "Difficulty", render: (f) => <DifficultyPips value={f.difficulty} /> },
    {
      key: "min",
      header: "Exp. minutes",
      align: "right",
      hideBelow: "sm",
      render: (f) => <span className="tabular text-xs">{f.expectedMinutes}'</span>,
    },
    {
      key: "proj",
      header: "Proj. score",
      align: "right",
      render: (f) => <span className="tabular text-xs">{f.projectedScore.toFixed(1)}</span>,
    },
  ];

  return (
    <>
      <Link
        to="/scout"
        className="mb-3 inline-flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-3" /> Back to Scout
      </Link>

      <Panel className="mb-4" bodyClassName="p-4">
        <div className="flex flex-wrap items-start gap-4">
          <div className="grid size-16 shrink-0 place-items-center rounded-lg border border-border bg-elevated text-lg font-semibold text-muted-foreground">
            {initials(p.name)}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-semibold tracking-tight text-foreground">{p.name}</h1>
              <RecommendationBadge value={p.recommendation} />
              <RiskBadge value={p.risk} />
              <AvailabilityBadge value={p.availability} />
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {p.position} · {p.age} yrs · {p.club} · {p.competition} · {p.nationality}
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-4">
              <div>
                <p className="label-caps">Market value</p>
                <p className="tabular text-base font-semibold text-foreground">
                  {eth(p.marketPrice)}
                </p>
              </div>
              <div>
                <p className="label-caps">7d change</p>
                <Delta value={p.priceChange7d} />
              </div>
              <div className="min-w-32">
                <p className="label-caps">Scout Score</p>
                <ScoutScore value={p.scoutScore} />
              </div>
            </div>
          </div>
          <Button
            size="sm"
            className="h-8 gap-1.5 text-xs"
            onClick={() => addToWatchlist.mutate()}
            disabled={addToWatchlist.isPending}
          >
            <Star className="size-3.5" /> Add to Watchlist
          </Button>
        </div>
      </Panel>

      <div className="panel mb-4 grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5">
        <Metric label="Average Score" value={p.averageScore.toFixed(1)} hint="Season to date" />
        <Metric label="Recent Form" value={p.form.toFixed(1)} hint="Last 5 gameweeks" />
        <Metric label="Projected Score" value={p.projectedScore.toFixed(1)} hint="PREDICTION" />
        <Metric label="Starting XI Prob." value={`${p.startingProbability}%`} hint="PREDICTION" />
        <Metric label="Minutes %" value={`${p.minutesShare}%`} hint="Share of available minutes" />
        <Metric label="Consistency" value={`${p.consistency}`} hint="Lower variance is better" />
        <Metric label="Ceiling" value={p.ceiling.toFixed(1)} hint="90th percentile outcome" />
        <Metric label="Floor" value={p.floor.toFixed(1)} hint="10th percentile outcome" />
        <Metric label="Risk" value={p.risk} hint="Composite risk rating" />
        <Metric
          label="Value ratio"
          value={(p.scoutScore / Math.max(0.2, p.marketPrice)).toFixed(1)}
          hint="Scout Score per Ξ"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Score history" subtitle="Actual score by gameweek — FACT" bodyClassName="p-3">
          <AreaTrend data={scoreData} xKey="gw" yKey="score" />
        </Panel>
        <Panel
          title="Projected vs actual"
          subtitle="Dashed line is the model PREDICTION"
          bodyClassName="p-3"
        >
          <MultiLine
            data={scoreData}
            xKey="gw"
            series={[
              { key: "score", color: "var(--color-primary)", name: "Actual" },
              { key: "projected", color: "var(--color-warning)", dashed: true, name: "Projected" },
            ]}
          />
        </Panel>
        <Panel title="Minutes played" subtitle="Per gameweek — FACT" bodyClassName="p-3">
          <Bars data={scoreData} xKey="gw" yKey="minutes" color="var(--color-chart-2)" />
        </Panel>
        <Panel
          title="Market price history"
          subtitle="90 days, limited floor price"
          bodyClassName="p-3"
        >
          {market.isLoading ? (
            <Skeleton className="h-[180px] w-full bg-muted" />
          ) : (
            <AreaTrend data={priceData} xKey="date" yKey="price" color="var(--color-chart-5)" />
          )}
        </Panel>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_340px]">
        <div className="min-w-0 space-y-4">
          <Panel title="Fixtures" subtitle="Next five matches with model projections">
            <DataTable
              columns={fixtureColumns}
              rows={fixtures.data ?? []}
              rowKey={(f) => f.fixture.id}
              isLoading={fixtures.isLoading}
              dense
            />
          </Panel>

          <Panel title="Scouting analysis" bodyClassName="p-4">
            <Tabs defaultValue="strengths">
              <TabsList className="h-8 bg-elevated">
                <TabsTrigger value="strengths" className="text-xs">
                  Strengths
                </TabsTrigger>
                <TabsTrigger value="weaknesses" className="text-xs">
                  Weaknesses
                </TabsTrigger>
                <TabsTrigger value="risk" className="text-xs">
                  Risk factors
                </TabsTrigger>
                <TabsTrigger value="model" className="text-xs">
                  Scout Score
                </TabsTrigger>
              </TabsList>
              <TabsContent value="strengths" className="mt-3">
                <ul className="space-y-2">
                  {p.analysis.strengths.map((s) => (
                    <li key={s} className="flex gap-2 text-xs text-foreground">
                      <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-positive" />
                      {s}
                    </li>
                  ))}
                </ul>
              </TabsContent>
              <TabsContent value="weaknesses" className="mt-3">
                <ul className="space-y-2">
                  {p.analysis.weaknesses.map((s) => (
                    <li key={s} className="flex gap-2 text-xs text-foreground">
                      <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-warning" />
                      {s}
                    </li>
                  ))}
                </ul>
              </TabsContent>
              <TabsContent value="risk" className="mt-3">
                <ul className="space-y-2">
                  {p.analysis.riskFactors.map((s) => (
                    <li key={s} className="flex gap-2 text-xs text-foreground">
                      <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-negative" />
                      {s}
                    </li>
                  ))}
                </ul>
              </TabsContent>
              <TabsContent value="model" className="mt-3 space-y-3">
                <p className="text-xs text-muted-foreground">{p.analysis.scoutScoreExplanation}</p>
                <div className="flex flex-wrap items-center gap-2">
                  <ProvenanceTag value="PREDICTION" />
                  <ConfidenceTag value={p.analysis.confidence} />
                </div>
              </TabsContent>
            </Tabs>
            <div className="mt-4 rounded-md border border-primary/30 bg-primary/8 px-3 py-2">
              <p className="label-caps text-primary">Opportunity</p>
              <p className="mt-1 text-xs text-foreground">{p.analysis.opportunity}</p>
            </div>
          </Panel>
        </div>

        <div className="space-y-4">
          <Panel title="Availability" bodyClassName="divide-y divide-border">
            <div className="px-4 py-3">
              <div className="flex items-center justify-between">
                <span className="label-caps">Status</span>
                <AvailabilityBadge value={p.availability} />
              </div>
              <div className="mt-2 flex items-center gap-2">
                <ProvenanceTag value={p.injury.provenance} />
                <span className="text-[11px] text-muted-foreground">
                  {p.injury.source} · {relativeTime(p.injury.updatedAt)}
                </span>
              </div>
            </div>
            <div className="px-4 py-3">
              <span className="label-caps">Injury detail</span>
              <p className="mt-1 text-xs text-foreground">
                {p.injury.description ?? "No active injury on record."}
              </p>
              {p.injury.expectedReturn && (
                <p className="mt-1.5 text-[11px] text-muted-foreground">
                  Expected return {dateTime(p.injury.expectedReturn)} —{" "}
                  <span className="text-primary">PREDICTION</span>
                </p>
              )}
            </div>
            <div className="px-4 py-3">
              <span className="label-caps">Suspension</span>
              <p className="mt-1 text-xs text-foreground">
                {p.suspension.suspended
                  ? `${p.suspension.reason} · ${p.suspension.matchesRemaining} match(es) remaining`
                  : "Not suspended."}
              </p>
            </div>
          </Panel>

          <Panel title="Market" bodyClassName="divide-y divide-border">
            {market.data ? (
              <>
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="label-caps">Current price</span>
                  <span className="tabular text-xs">{eth(market.data.currentPrice)}</span>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="label-caps">Lowest available</span>
                  <span className="tabular text-xs">{eth(market.data.lowestAsk)}</span>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="label-caps">24h / 7d / 30d</span>
                  <span className="flex items-center gap-2">
                    <Delta value={market.data.change24h} />
                    <Delta value={market.data.change7d} />
                    <Delta value={market.data.change30d} />
                  </span>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="label-caps">7d volume</span>
                  <span className="tabular text-xs">{market.data.volume7d} sales</span>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5">
                  <span className="label-caps">Trend</span>
                  <Tag
                    tone={
                      market.data.trend === "UP"
                        ? "positive"
                        : market.data.trend === "DOWN"
                          ? "negative"
                          : "muted"
                    }
                  >
                    {market.data.trend}
                  </Tag>
                </div>
              </>
            ) : (
              <div className="p-4">
                <Skeleton className="h-24 w-full bg-muted" />
              </div>
            )}
          </Panel>

          <Panel title="Consistency profile" bodyClassName="space-y-3 p-4">
            {[
              ["Consistency", p.consistency],
              ["Minutes share", p.minutesShare],
              ["Starting XI probability", p.startingProbability],
            ].map(([label, value]) => (
              <div key={String(label)}>
                <p className="text-[11px] text-muted-foreground">{label}</p>
                <div className="mt-1">
                  <ScoreBar value={Number(value)} />
                </div>
              </div>
            ))}
          </Panel>
        </div>
      </div>
    </>
  );
}
