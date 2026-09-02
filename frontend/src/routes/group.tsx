import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { PageHeader } from "@/components/layout/AppShell";
import { DataTable, type Column } from "@/components/scoutlab/DataTable";
import { ErrorState, KpiCard, KpiSkeleton, Panel } from "@/components/scoutlab/primitives";
import { Bars } from "@/components/scoutlab/charts";
import { groupQuery } from "@/services/queries";
import { eth } from "@/lib/format";
import type { GroupMember } from "@/types";

export const Route = createFileRoute("/group")({
  head: () => ({
    meta: [
      { title: "Group — Private League Leaderboard | ScoutLab" },
      {
        name: "description",
        content:
          "Private ScoutLab group of 10 managers: gameweek points, overall standings, squad value and rank movement.",
      },
      { property: "og:title", content: "Group — Private League Leaderboard | ScoutLab" },
      {
        property: "og:description",
        content: "Leaderboard and performance comparison for the private ScoutLab group.",
      },
    ],
  }),
  component: GroupPage,
});

function RankDelta({ member }: { member: GroupMember }) {
  const diff = member.previousRank - member.rank;
  const Icon = diff > 0 ? ArrowUpRight : diff < 0 ? ArrowDownRight : Minus;
  return (
    <span
      className={
        diff > 0
          ? "tabular inline-flex items-center gap-0.5 text-xs text-positive"
          : diff < 0
            ? "tabular inline-flex items-center gap-0.5 text-xs text-negative"
            : "tabular inline-flex items-center gap-0.5 text-xs text-muted-foreground"
      }
    >
      <Icon className="size-3" />
      {diff === 0 ? "—" : Math.abs(diff)}
    </span>
  );
}

function GroupPage() {
  const group = useQuery(groupQuery);
  const members = group.data ?? [];

  const columns: Column<GroupMember>[] = [
    {
      key: "rank",
      header: "#",
      width: "48px",
      render: (m) => <span className="tabular text-xs font-semibold text-foreground">{m.rank}</span>,
    },
    {
      key: "user",
      header: "Manager",
      render: (m) => (
        <span className="flex items-center gap-2">
          <span className="grid size-6 place-items-center rounded bg-primary/15 text-[10px] font-semibold text-primary uppercase">
            {m.username.slice(0, 2)}
          </span>
          <span className="text-xs text-foreground">{m.username}</span>
        </span>
      ),
    },
    {
      key: "gw",
      header: "GW points",
      align: "right",
      render: (m) => <span className="tabular text-xs">{m.gameweekPoints.toFixed(0)}</span>,
    },
    {
      key: "overall",
      header: "Overall",
      align: "right",
      render: (m) => (
        <span className="tabular text-xs font-medium text-foreground">
          {m.overallPoints.toFixed(0)}
        </span>
      ),
    },
    {
      key: "value",
      header: "Squad value",
      align: "right",
      hideBelow: "sm",
      render: (m) => <span className="tabular text-xs">{eth(m.squadValue, 1)}</span>,
    },
    {
      key: "cards",
      header: "Cards",
      align: "right",
      hideBelow: "md",
      render: (m) => <span className="tabular text-xs">{m.cards}</span>,
    },
    { key: "delta", header: "Move", align: "right", render: (m) => <RankDelta member={m} /> },
  ];

  const chartData = members.map((m) => ({ user: m.username, points: m.gameweekPoints }));

  return (
    <>
      <PageHeader title="Group" description="Private league of 10 managers" />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {group.isLoading || members.length === 0 ? (
          <KpiSkeleton count={4} />
        ) : (
          <>
            <KpiCard label="Managers" value={String(members.length)} />
            <KpiCard label="Leader" value={members[0]!.username} tone="positive" />
            <KpiCard
              label="Avg GW points"
              value={(members.reduce((s, m) => s + m.gameweekPoints, 0) / members.length).toFixed(0)}
            />
            <KpiCard
              label="Combined squad value"
              value={eth(members.reduce((s, m) => s + m.squadValue, 0), 1)}
            />
          </>
        )}
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_400px]">
        <Panel title="Leaderboard" subtitle="Overall standings">
          {group.isError ? (
            <ErrorState onRetry={() => void group.refetch()} />
          ) : (
            <DataTable
              columns={columns}
              rows={members}
              rowKey={(m) => m.id}
              isLoading={group.isLoading}
            />
          )}
        </Panel>
        <Panel title="Gameweek points" subtitle="Current gameweek comparison" bodyClassName="p-3">
          <Bars data={chartData} xKey="user" yKey="points" height={280} />
        </Panel>
      </div>
    </>
  );
}
