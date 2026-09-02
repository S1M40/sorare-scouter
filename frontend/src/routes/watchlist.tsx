import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Star, X } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/layout/AppShell";
import { DataTable, type Column } from "@/components/scoutlab/DataTable";
import {
  Delta,
  EmptyState,
  ErrorState,
  Panel,
  RiskBadge,
  ScoutScore,
} from "@/components/scoutlab/primitives";
import { PlayerIdentity, PositionTag } from "@/components/scoutlab/PlayerIdentity";
import { Button } from "@/components/ui/button";
import { api } from "@/services/api";
import { qk, watchlistQuery } from "@/services/queries";
import { eth } from "@/lib/format";
import type { WatchlistEntry } from "@/types";

export const Route = createFileRoute("/watchlist")({
  head: () => ({
    meta: [
      { title: "Watchlist — Tracked Targets | ScoutLab" },
      {
        name: "description",
        content:
          "Your tracked Sorare targets with live price, 7-day change, Scout Score, form, starting probability, risk and the latest alert.",
      },
      { property: "og:title", content: "Watchlist — Tracked Targets | ScoutLab" },
      {
        property: "og:description",
        content: "Monitor scouting targets and price triggers before you commit capital.",
      },
    ],
  }),
  component: WatchlistPage,
});

function WatchlistPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const watchlist = useQuery(watchlistQuery);

  const remove = useMutation({
    mutationFn: (playerId: string) => api.removeFromWatchlist(playerId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: qk.watchlist });
      toast("Removed from watchlist");
    },
  });

  const columns: Column<WatchlistEntry>[] = [
    { key: "player", header: "Player", width: "210px", render: (w) => <PlayerIdentity player={w.player} /> },
    { key: "pos", header: "Pos", render: (w) => <PositionTag value={w.player.position} /> },
    {
      key: "price",
      header: "Price",
      align: "right",
      render: (w) => <span className="tabular text-xs">{eth(w.player.marketPrice)}</span>,
    },
    {
      key: "change",
      header: "7d",
      align: "right",
      render: (w) => <Delta value={w.player.priceChange7d} />,
    },
    {
      key: "target",
      header: "Target",
      align: "right",
      hideBelow: "md",
      render: (w) => (
        <span className="tabular text-xs text-muted-foreground">
          {w.targetPrice ? eth(w.targetPrice) : "—"}
        </span>
      ),
    },
    { key: "scout", header: "Scout", render: (w) => <ScoutScore value={w.player.scoutScore} /> },
    {
      key: "form",
      header: "Form",
      align: "right",
      hideBelow: "sm",
      render: (w) => <span className="tabular text-xs">{w.player.form.toFixed(1)}</span>,
    },
    {
      key: "startxi",
      header: "Start XI",
      hideBelow: "lg",
      render: (w) => <ScoutScore value={w.player.startingProbability} />,
    },
    { key: "risk", header: "Risk", hideBelow: "lg", render: (w) => <RiskBadge value={w.player.risk} /> },
    {
      key: "alert",
      header: "Latest alert",
      hideBelow: "xl",
      render: (w) => (
        <span className="text-[11px] text-muted-foreground">{w.latestAlert ?? "No alerts yet"}</span>
      ),
    },
    {
      key: "actions",
      header: "",
      align: "right",
      render: (w) => (
        <Button
          variant="ghost"
          size="sm"
          className="size-7 p-0 text-muted-foreground hover:text-negative"
          onClick={(e) => {
            e.stopPropagation();
            remove.mutate(w.playerId);
          }}
          aria-label={`Remove ${w.player.name}`}
        >
          <X className="size-3.5" />
        </Button>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Watchlist"
        description="Targets you are tracking before committing capital"
        actions={
          <Button size="sm" className="h-8 gap-1.5 text-xs" onClick={() => void navigate({ to: "/scout" })}>
            <Star className="size-3.5" /> Find players
          </Button>
        }
      />

      <Panel>
        {watchlist.isError ? (
          <ErrorState onRetry={() => void watchlist.refetch()} />
        ) : watchlist.data?.length === 0 ? (
          <EmptyState
            icon={Star}
            title="Your watchlist is empty"
            description="Add players from the Scout page or a player profile to track price moves, form and starting XI signals here."
            action={
              <Button size="sm" className="h-8 text-xs" onClick={() => void navigate({ to: "/scout" })}>
                Open Scout
              </Button>
            }
          />
        ) : (
          <DataTable
            columns={columns}
            rows={watchlist.data ?? []}
            rowKey={(w) => w.id}
            isLoading={watchlist.isLoading}
            onRowClick={(w) =>
              void navigate({ to: "/players/$playerId", params: { playerId: w.playerId } })
            }
          />
        )}
      </Panel>
    </>
  );
}
