import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/layout/AppShell";
import {
  CategoryTag,
  ConfidenceTag,
  EmptyState,
  ErrorState,
  Panel,
  ProvenanceTag,
  Tag,
} from "@/components/scoutlab/primitives";
import { newsQuery } from "@/services/queries";
import { relativeTime } from "@/lib/format";
import type { NewsCategory } from "@/types";

const categories: (NewsCategory | "All")[] = [
  "All",
  "Transfer",
  "Injury",
  "Starting XI",
  "Suspension",
  "Performance",
  "Club News",
];

export const Route = createFileRoute("/news")({
  head: () => ({
    meta: [
      { title: "News — Football Intelligence Feed | ScoutLab" },
      {
        name: "description",
        content:
          "Curated football intelligence feed with source attribution, category tags and explicit fact, report and prediction labelling.",
      },
      { property: "og:title", content: "News — Football Intelligence Feed | ScoutLab" },
      {
        property: "og:description",
        content: "Injury, transfer, starting XI and performance intelligence with confidence ratings.",
      },
    ],
  }),
  component: NewsPage,
});

function NewsPage() {
  const [category, setCategory] = useState<(typeof categories)[number]>("All");
  const news = useQuery(newsQuery(category === "All" ? undefined : category));

  return (
    <>
      <PageHeader
        title="News"
        description="Intelligence feed with explicit source attribution"
        meta={
          <span className="text-[11px] text-muted-foreground">
            FACT = confirmed · REPORT = credible but unconfirmed · PREDICTION = ScoutLab model
          </span>
        }
        actions={
          <div className="flex flex-wrap gap-1.5">
            {categories.map((c) => (
              <button key={c} type="button" onClick={() => setCategory(c)}>
                <Tag tone={category === c ? "primary" : "muted"} className="normal-case tracking-normal">
                  {c}
                </Tag>
              </button>
            ))}
          </div>
        }
      />

      <Panel>
        {news.isError ? (
          <ErrorState onRetry={() => void news.refetch()} />
        ) : news.data?.length === 0 ? (
          <EmptyState title="No stories" description="Nothing filed in this category yet." />
        ) : (
          <ul className="divide-y divide-border">
            {(news.data ?? []).map((n) => (
              <li key={n.id} className="px-4 py-3.5 transition-colors hover:bg-accent/40">
                <div className="flex flex-wrap items-center gap-2">
                  <CategoryTag value={n.category} />
                  <ProvenanceTag value={n.provenance} />
                  <ConfidenceTag value={n.confidence} />
                  <span className="tabular ml-auto text-[10px] text-muted-foreground">
                    {relativeTime(n.publishedAt)}
                  </span>
                </div>
                <h3 className="mt-2 text-sm font-medium text-foreground">{n.headline}</h3>
                <p className="mt-1 text-xs text-muted-foreground">{n.summary}</p>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                  <span className="text-foreground">{n.source}</span>
                  {n.playerId && (
                    <>
                      <span>·</span>
                      <Link
                        to="/players/$playerId"
                        params={{ playerId: n.playerId }}
                        className="text-primary hover:underline"
                      >
                        {n.playerName}
                      </Link>
                    </>
                  )}
                  {n.club && (
                    <>
                      <span>·</span>
                      <span>{n.club}</span>
                    </>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </>
  );
}
