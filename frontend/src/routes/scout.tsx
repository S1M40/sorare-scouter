import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/AppShell";
import { ScoutExplorer } from "@/components/scoutlab/ScoutExplorer";
import { Tag } from "@/components/scoutlab/primitives";

export const Route = createFileRoute("/scout")({
  head: () => ({
    meta: [
      { title: "Scout — Advanced Player Screening | ScoutLab" },
      {
        name: "description",
        content:
          "Screen the Sorare player universe by position, competition, form, projected score, starting XI probability, price and Scout Score.",
      },
      { property: "og:title", content: "Scout — Advanced Player Screening | ScoutLab" },
      {
        property: "og:description",
        content:
          "Multi-filter scouting workspace with sortable results, saved views and full scouting profiles.",
      },
    ],
  }),
  component: ScoutPage,
});

function ScoutPage() {
  return (
    <>
      <PageHeader
        title="Scout"
        description="Screen 180 tracked players across 6 competitions"
        meta={
          <>
            <Tag tone="primary">Model v2.4</Tag>
            <Tag tone="muted">Projections update every 15 min</Tag>
          </>
        }
      />
      <ScoutExplorer title="Results" pageSize={20} />
    </>
  );
}
