import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/AppShell";
import { ScoutExplorer } from "@/components/scoutlab/ScoutExplorer";

export const Route = createFileRoute("/players/")({
  head: () => ({
    meta: [
      { title: "Players — Tracked Universe | ScoutLab" },
      {
        name: "description",
        content:
          "Browse every player tracked by ScoutLab with average score, form, minutes share, availability and market price.",
      },
      { property: "og:title", content: "Players — Tracked Universe | ScoutLab" },
      {
        property: "og:description",
        content: "The full ScoutLab player database with sortable performance and market columns.",
      },
    ],
  }),
  component: PlayersPage,
});

function PlayersPage() {
  return (
    <>
      <PageHeader title="Players" description="Full tracked universe with performance and market columns" />
      <ScoutExplorer title="All players" pageSize={25} />
    </>
  );
}
