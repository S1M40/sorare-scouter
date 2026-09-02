import { useMemo, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, RotateCcw, Save, SlidersHorizontal } from "lucide-react";
import { toast } from "sonner";
import { Panel, RecommendationBadge, RiskBadge, ScoutScore, Tag, Delta, ErrorState } from "./primitives";
import { DataTable, type Column } from "./DataTable";
import { PlayerIdentity, PositionTag } from "./PlayerIdentity";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { clubsQuery, competitionsQuery, scoutQuery } from "@/services/queries";
import { eth } from "@/lib/format";
import type { Player, Position, Recommendation, RiskLevel, SavedFilter, ScoutFilters } from "@/types";

const positions: Position[] = ["GK", "DEF", "MID", "FWD"];
const recommendations: Recommendation[] = ["BUY", "WATCH", "HOLD", "SELL", "AVOID"];
const risks: RiskLevel[] = ["LOW", "MEDIUM", "HIGH"];

const defaults: ScoutFilters = {
  search: "",
  positions: [],
  clubs: [],
  competitions: [],
  ageMax: 40,
  priceMax: 60,
  minAverageScore: 0,
  minForm: 0,
  minProjected: 0,
  minStartingProbability: 0,
  minMinutesShare: 0,
  excludeInjured: false,
  excludeSuspended: false,
  minScoutScore: 0,
  risk: [],
  recommendations: [],
};

function FilterControls({
  filters,
  set,
}: {
  filters: ScoutFilters;
  set: (patch: Partial<ScoutFilters>) => void;
}) {
  const { data: clubs } = useQuery(clubsQuery);
  const { data: competitions } = useQuery(competitionsQuery);

  const toggle = <T,>(list: T[] | undefined, value: T): T[] =>
    (list ?? []).includes(value) ? (list ?? []).filter((v) => v !== value) : [...(list ?? []), value];

  const sliders: { key: keyof ScoutFilters; label: string; max: number; suffix?: string }[] = [
    { key: "minScoutScore", label: "Min Scout Score", max: 100 },
    { key: "minAverageScore", label: "Min Average Score", max: 90 },
    { key: "minForm", label: "Min Form", max: 90 },
    { key: "minProjected", label: "Min Projected Score", max: 90 },
    { key: "minStartingProbability", label: "Min Starting XI %", max: 100, suffix: "%" },
    { key: "minMinutesShare", label: "Min Minutes %", max: 100, suffix: "%" },
    { key: "ageMax", label: "Max Age", max: 40 },
    { key: "priceMax", label: "Max Price (Ξ)", max: 60 },
  ];

  return (
    <div className="space-y-5">
      <div>
        <p className="label-caps mb-1.5">Position</p>
        <div className="flex flex-wrap gap-1.5">
          {positions.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => set({ positions: toggle(filters.positions, p) })}
              className="rounded-sm"
            >
              <Tag tone={filters.positions?.includes(p) ? "primary" : "muted"}>{p}</Tag>
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-2">
        <div>
          <p className="label-caps mb-1.5">Competition</p>
          <Select
            value={filters.competitions?.[0] ?? "all"}
            onValueChange={(v) => set({ competitions: v === "all" ? [] : [v] })}
          >
            <SelectTrigger className="h-8 text-xs">
              <SelectValue placeholder="All competitions" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All competitions</SelectItem>
              {competitions?.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <p className="label-caps mb-1.5">Club</p>
          <Select
            value={filters.clubs?.[0] ?? "all"}
            onValueChange={(v) => set({ clubs: v === "all" ? [] : [v] })}
          >
            <SelectTrigger className="h-8 text-xs">
              <SelectValue placeholder="All clubs" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All clubs</SelectItem>
              {clubs?.map((c) => (
                <SelectItem key={c.id} value={c.name}>
                  {c.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-3">
        {sliders.map((s) => (
          <div key={String(s.key)}>
            <div className="flex items-center justify-between">
              <Label className="text-[11px] text-muted-foreground">{s.label}</Label>
              <span className="tabular text-[11px] text-foreground">
                {String(filters[s.key] ?? 0)}
                {s.suffix ?? ""}
              </span>
            </div>
            <Slider
              className="mt-1.5"
              value={[Number(filters[s.key] ?? 0)]}
              min={0}
              max={s.max}
              step={1}
              onValueChange={([v]) => set({ [s.key]: v } as Partial<ScoutFilters>)}
            />
          </div>
        ))}
      </div>

      <div>
        <p className="label-caps mb-1.5">Recommendation</p>
        <div className="flex flex-wrap gap-1.5">
          {recommendations.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => set({ recommendations: toggle(filters.recommendations, r) })}
            >
              <Tag tone={filters.recommendations?.includes(r) ? "primary" : "muted"}>{r}</Tag>
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="label-caps mb-1.5">Risk</p>
        <div className="flex flex-wrap gap-1.5">
          {risks.map((r) => (
            <button key={r} type="button" onClick={() => set({ risk: toggle(filters.risk, r) })}>
              <Tag tone={filters.risk?.includes(r) ? "primary" : "muted"}>{r}</Tag>
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2.5 border-t border-border pt-4">
        <div className="flex items-center justify-between">
          <Label className="text-[11px] text-muted-foreground">Exclude injured / doubtful</Label>
          <Switch
            checked={!!filters.excludeInjured}
            onCheckedChange={(v) => set({ excludeInjured: v })}
          />
        </div>
        <div className="flex items-center justify-between">
          <Label className="text-[11px] text-muted-foreground">Exclude suspended</Label>
          <Switch
            checked={!!filters.excludeSuspended}
            onCheckedChange={(v) => set({ excludeSuspended: v })}
          />
        </div>
      </div>
    </div>
  );
}

export function ScoutExplorer({
  title = "Scout",
  pageSize = 20,
}: {
  title?: string;
  pageSize?: number;
}) {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ScoutFilters>(defaults);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<keyof Player>("scoutScore");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [saved, setSaved] = useState<SavedFilter[]>([]);

  const set = (patch: Partial<ScoutFilters>) => {
    setFilters((f) => ({ ...f, ...patch }));
    setPage(1);
  };

  const query = useQuery(scoutQuery({ ...filters, page, pageSize, sortBy, sortDir }));
  const rows = query.data?.items ?? [];
  const total = query.data?.total ?? 0;
  const pages = Math.max(1, Math.ceil(total / pageSize));

  const onSort = (key: string) => {
    if (key === sortBy) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortBy(key as keyof Player);
      setSortDir("desc");
    }
  };

  const columns = useMemo<Column<Player>[]>(
    () => [
      {
        key: "name",
        header: "Player",
        sortable: true,
        width: "220px",
        render: (p) => <PlayerIdentity player={p} />,
      },
      {
        key: "position",
        header: "Pos",
        sortable: true,
        render: (p) => <PositionTag value={p.position} />,
      },
      {
        key: "age",
        header: "Age",
        align: "right",
        sortable: true,
        hideBelow: "md",
        render: (p) => <span className="tabular text-xs">{p.age}</span>,
      },
      {
        key: "averageScore",
        header: "Avg",
        align: "right",
        sortable: true,
        render: (p) => <span className="tabular text-xs">{p.averageScore.toFixed(1)}</span>,
      },
      {
        key: "form",
        header: "Form",
        align: "right",
        sortable: true,
        hideBelow: "sm",
        render: (p) => (
          <span
            className={
              p.form >= p.averageScore
                ? "tabular text-xs text-positive"
                : "tabular text-xs text-negative"
            }
          >
            {p.form.toFixed(1)}
          </span>
        ),
      },
      {
        key: "projectedScore",
        header: "Proj",
        align: "right",
        sortable: true,
        hideBelow: "md",
        render: (p) => <span className="tabular text-xs">{p.projectedScore.toFixed(1)}</span>,
      },
      {
        key: "startingProbability",
        header: "Start XI",
        sortable: true,
        hideBelow: "lg",
        render: (p) => <ScoutScore value={p.startingProbability} />,
      },
      {
        key: "marketPrice",
        header: "Price",
        align: "right",
        sortable: true,
        render: (p) => <span className="tabular text-xs">{eth(p.marketPrice)}</span>,
      },
      {
        key: "priceChange7d",
        header: "7d",
        align: "right",
        sortable: true,
        hideBelow: "lg",
        render: (p) => <Delta value={p.priceChange7d} />,
      },
      {
        key: "scoutScore",
        header: "Scout",
        sortable: true,
        render: (p) => <ScoutScore value={p.scoutScore} />,
      },
      {
        key: "risk",
        header: "Risk",
        sortable: true,
        hideBelow: "xl",
        render: (p) => <RiskBadge value={p.risk} />,
      },
      {
        key: "recommendation",
        header: "Call",
        sortable: true,
        render: (p) => <RecommendationBadge value={p.recommendation} />,
      },
    ],
    [],
  );

  const controls = <FilterControls filters={filters} set={set} />;

  return (
    <div className="grid gap-4 xl:grid-cols-[248px_1fr]">
      <aside className="hidden xl:block">
        <Panel title="Filters" bodyClassName="p-4">
          {controls}
        </Panel>
      </aside>

      <div className="min-w-0 space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Input
            value={filters.search ?? ""}
            onChange={(e) => set({ search: e.target.value })}
            placeholder="Search player or club…"
            className="h-8 max-w-xs text-xs"
          />
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs xl:hidden">
                <SlidersHorizontal className="size-3.5" /> Filters
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[300px] overflow-y-auto">
              <SheetHeader>
                <SheetTitle className="text-sm">Filters</SheetTitle>
              </SheetHeader>
              <div className="px-4 pb-8">{controls}</div>
            </SheetContent>
          </Sheet>
          <Button
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-xs"
            onClick={() => {
              const entry: SavedFilter = {
                id: `sf-${saved.length + 1}`,
                name: `View ${saved.length + 1}`,
                filters,
              };
              setSaved((s) => [...s, entry]);
              toast.success("Filter view saved", { description: entry.name });
            }}
          >
            <Save className="size-3.5" /> Save filters
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 gap-1.5 text-xs"
            onClick={() => {
              setFilters(defaults);
              setPage(1);
              toast("Filters reset");
            }}
          >
            <RotateCcw className="size-3.5" /> Reset
          </Button>
          <span className="tabular ml-auto text-xs text-muted-foreground">
            {total} players match
          </span>
        </div>

        {saved.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="label-caps">Saved</span>
            {saved.map((s) => (
              <button key={s.id} type="button" onClick={() => setFilters(s.filters)}>
                <Tag tone="primary" className="normal-case">
                  {s.name}
                </Tag>
              </button>
            ))}
          </div>
        )}

        <Panel title={title} subtitle="Click a row to open the full scouting profile">
          {query.isError ? (
            <ErrorState onRetry={() => void query.refetch()} />
          ) : (
            <DataTable
              columns={columns}
              rows={rows}
              rowKey={(p) => p.id}
              isLoading={query.isLoading}
              sortBy={sortBy}
              sortDir={sortDir}
              onSort={onSort}
              onRowClick={(p) =>
                void navigate({ to: "/players/$playerId", params: { playerId: p.id } })
              }
            />
          )}
          <div className="flex items-center justify-between border-t border-border px-3 py-2">
            <span className="tabular text-[11px] text-muted-foreground">
              Page {page} of {pages}
            </span>
            <div className="flex items-center gap-1.5">
              <Button
                variant="outline"
                size="sm"
                className="h-7 px-2"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                <ChevronLeft className="size-3.5" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 px-2"
                disabled={page >= pages}
                onClick={() => setPage((p) => p + 1)}
              >
                <ChevronRight className="size-3.5" />
              </Button>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
