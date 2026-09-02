import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/layout/AppShell";
import { DataTable, type Column } from "@/components/scoutlab/DataTable";
import { DifficultyPips, ErrorState, Panel, Tag } from "@/components/scoutlab/primitives";
import { PositionTag } from "@/components/scoutlab/PlayerIdentity";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  clubsQuery,
  competitionsQuery,
  fixturesQuery,
  gameweeksQuery,
  scoutQuery,
} from "@/services/queries";
import { dateTime } from "@/lib/format";
import type { Fixture, Player, Position } from "@/types";

export const Route = createFileRoute("/fixtures")({
  head: () => ({
    meta: [
      { title: "Fixtures — Gameweek Difficulty & Projections | ScoutLab" },
      {
        name: "description",
        content:
          "Fixture intelligence by gameweek: match dates, competition, difficulty ratings, player availability and projected scores.",
      },
      { property: "og:title", content: "Fixtures — Gameweek Difficulty & Projections | ScoutLab" },
      {
        property: "og:description",
        content: "Plan line-ups with ScoutLab fixture difficulty and projected score models.",
      },
    ],
  }),
  component: FixturesPage,
});

function FixturesPage() {
  const gameweeks = useQuery(gameweeksQuery);
  const clubs = useQuery(clubsQuery);
  const competitions = useQuery(competitionsQuery);

  const [gameweek, setGameweek] = useState<string>("current");
  const [competition, setCompetition] = useState<string>("all");
  const [clubId, setClubId] = useState<string>("all");
  const [position, setPosition] = useState<string>("all");

  const activeGw =
    gameweek === "current" ? gameweeks.data?.[0]?.id : Number.parseInt(gameweek, 10);

  const fixtures = useQuery(
    fixturesQuery({
      gameweek: activeGw,
      competition: competition === "all" ? undefined : competition,
      clubId: clubId === "all" ? undefined : clubId,
    }),
  );

  const club = clubs.data?.find((c) => c.id === clubId);
  const players = useQuery(
    scoutQuery({
      clubs: club ? [club.name] : [],
      competitions: competition === "all" ? [] : [competition],
      positions: position === "all" ? [] : [position as Position],
      pageSize: 12,
      sortBy: "projectedScore",
    }),
  );

  const columns: Column<Fixture>[] = [
    { key: "gw", header: "GW", render: (f) => <span className="tabular text-xs">{f.gameweek}</span> },
    {
      key: "match",
      header: "Match",
      width: "260px",
      render: (f) => (
        <span className="text-xs text-foreground">
          {f.homeClub} <span className="text-muted-foreground">vs</span> {f.awayClub}
        </span>
      ),
    },
    {
      key: "comp",
      header: "Competition",
      hideBelow: "md",
      render: (f) => <span className="text-xs text-muted-foreground">{f.competition}</span>,
    },
    {
      key: "date",
      header: "Kick-off",
      hideBelow: "sm",
      render: (f) => <span className="tabular text-xs">{dateTime(f.date)}</span>,
    },
    { key: "diff", header: "Difficulty", render: (f) => <DifficultyPips value={f.difficulty} /> },
  ];

  const playerColumns: Column<Player>[] = [
    {
      key: "player",
      header: "Player",
      render: (p) => <span className="text-xs text-foreground">{p.name}</span>,
    },
    { key: "pos", header: "Pos", render: (p) => <PositionTag value={p.position} /> },
    {
      key: "club",
      header: "Club",
      hideBelow: "md",
      render: (p) => <span className="text-xs text-muted-foreground">{p.club}</span>,
    },
    {
      key: "avail",
      header: "Availability",
      render: (p) => (
        <Tag
          tone={
            p.availability === "AVAILABLE"
              ? "positive"
              : p.availability === "DOUBTFUL"
                ? "warning"
                : "negative"
          }
        >
          {p.availability}
        </Tag>
      ),
    },
    {
      key: "proj",
      header: "Proj",
      align: "right",
      render: (p) => <span className="tabular text-xs">{p.projectedScore.toFixed(1)}</span>,
    },
  ];

  return (
    <>
      <PageHeader
        title="Fixtures"
        description="Gameweek schedule, difficulty ratings and projected output"
        meta={
          <>
            <Tag tone="primary">{gameweeks.data?.[0]?.label ?? "GW —"} live</Tag>
            <Tag tone="muted">Difficulty 1 (easiest) to 5 (hardest)</Tag>
          </>
        }
        actions={
          <div className="flex flex-wrap gap-2">
            <Select value={gameweek} onValueChange={setGameweek}>
              <SelectTrigger className="h-8 w-28 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="current">Current GW</SelectItem>
                {gameweeks.data?.map((g) => (
                  <SelectItem key={g.id} value={String(g.id)}>
                    {g.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={competition} onValueChange={setCompetition}>
              <SelectTrigger className="h-8 w-36 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All competitions</SelectItem>
                {competitions.data?.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={clubId} onValueChange={setClubId}>
              <SelectTrigger className="h-8 w-36 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All clubs</SelectItem>
                {clubs.data?.map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={position} onValueChange={setPosition}>
              <SelectTrigger className="h-8 w-24 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All pos</SelectItem>
                {["GK", "DEF", "MID", "FWD"].map((p) => (
                  <SelectItem key={p} value={p}>
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[1fr_380px]">
        <Panel title="Schedule" subtitle="Filtered fixture list">
          {fixtures.isError ? (
            <ErrorState onRetry={() => void fixtures.refetch()} />
          ) : (
            <DataTable
              columns={columns}
              rows={fixtures.data ?? []}
              rowKey={(f) => f.id}
              isLoading={fixtures.isLoading}
              emptyTitle="No fixtures"
              emptyDescription="No matches match the current filters."
            />
          )}
        </Panel>

        <Panel title="Player projections" subtitle="Top projected scores for this selection">
          <DataTable
            columns={playerColumns}
            rows={players.data?.items ?? []}
            rowKey={(p) => p.id}
            isLoading={players.isLoading}
            dense
          />
        </Panel>
      </div>
    </>
  );
}
