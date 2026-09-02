import type { ReactNode } from "react";
import { ArrowDownRight, ArrowRight, ArrowUpRight, Inbox, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { signedPct, toneForDelta } from "@/lib/format";
import type {
  AlertCategory,
  AvailabilityStatus,
  Confidence,
  NewsCategory,
  Provenance,
  Rarity,
  Recommendation,
  RiskLevel,
} from "@/types";

/* ------------------------------- Panel ------------------------------- */
export function Panel({
  title,
  subtitle,
  actions,
  children,
  className,
  bodyClassName,
}: {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <section className={cn("panel overflow-hidden", className)}>
      {(title || actions) && (
        <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
          <div className="min-w-0">
            {title && (
              <h2 className="truncate text-sm font-semibold tracking-tight text-foreground">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="truncate text-xs text-muted-foreground">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
        </header>
      )}
      <div className={cn(bodyClassName)}>{children}</div>
    </section>
  );
}

/* ------------------------------- Chips ------------------------------- */
const chip =
  "inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[10.5px] font-semibold uppercase tracking-wider leading-none";

export function Tag({
  children,
  tone = "neutral",
  className,
}: {
  children: ReactNode;
  tone?: "neutral" | "primary" | "positive" | "warning" | "negative" | "muted";
  className?: string;
}) {
  const tones: Record<string, string> = {
    neutral: "border-border-strong bg-elevated text-foreground",
    muted: "border-border bg-muted text-muted-foreground",
    primary: "border-primary/40 bg-primary/12 text-primary",
    positive: "border-positive/40 bg-positive/12 text-positive",
    warning: "border-warning/40 bg-warning/12 text-warning",
    negative: "border-negative/45 bg-negative/12 text-negative",
  };
  return <span className={cn(chip, tones[tone], className)}>{children}</span>;
}

const recTone: Record<Recommendation, "primary" | "positive" | "warning" | "negative" | "muted"> = {
  BUY: "positive",
  WATCH: "primary",
  HOLD: "muted",
  SELL: "warning",
  AVOID: "negative",
};
export const RecommendationBadge = ({ value }: { value: Recommendation }) => (
  <Tag tone={recTone[value]}>{value}</Tag>
);

const riskTone: Record<RiskLevel, "positive" | "warning" | "negative"> = {
  LOW: "positive",
  MEDIUM: "warning",
  HIGH: "negative",
};
export const RiskBadge = ({ value }: { value: RiskLevel }) => (
  <Tag tone={riskTone[value]}>{value} risk</Tag>
);

const availTone: Record<AvailabilityStatus, "positive" | "warning" | "negative" | "muted"> = {
  AVAILABLE: "positive",
  DOUBTFUL: "warning",
  INJURED: "negative",
  SUSPENDED: "negative",
  UNAVAILABLE: "muted",
};
export function AvailabilityBadge({ value }: { value: AvailabilityStatus }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className={cn(
          "size-1.5 rounded-full",
          value === "AVAILABLE" && "bg-positive",
          value === "DOUBTFUL" && "bg-warning",
          (value === "INJURED" || value === "SUSPENDED") && "bg-negative",
          value === "UNAVAILABLE" && "bg-neutral",
        )}
      />
      <Tag tone={availTone[value]}>{value}</Tag>
    </span>
  );
}

const provTone: Record<Provenance, "positive" | "warning" | "primary"> = {
  FACT: "positive",
  REPORT: "warning",
  PREDICTION: "primary",
};
export const ProvenanceTag = ({ value }: { value: Provenance }) => (
  <Tag tone={provTone[value]}>{value}</Tag>
);

export const ConfidenceTag = ({ value }: { value: Confidence }) => (
  <Tag tone={value === "HIGH" ? "positive" : value === "MEDIUM" ? "warning" : "muted"}>
    {value} confidence
  </Tag>
);

export const RarityTag = ({ value }: { value: Rarity }) => (
  <Tag tone={value === "super rare" ? "primary" : value === "rare" ? "warning" : "muted"}>
    {value}
  </Tag>
);

export const CategoryTag = ({ value }: { value: NewsCategory | AlertCategory }) => (
  <Tag tone="neutral" className="normal-case tracking-normal">
    {value}
  </Tag>
);

/* ------------------------------- Delta ------------------------------- */
export function Delta({ value, suffix = "%" }: { value: number; suffix?: string }) {
  const Icon = value > 0 ? ArrowUpRight : value < 0 ? ArrowDownRight : ArrowRight;
  return (
    <span className={cn("tabular inline-flex items-center gap-0.5 text-xs", toneForDelta(value))}>
      <Icon className="size-3" />
      {suffix === "%" ? signedPct(value) : `${value > 0 ? "+" : ""}${value.toFixed(2)}${suffix}`}
    </span>
  );
}

/* ------------------------------ KPI card ----------------------------- */
export function KpiCard({
  label,
  value,
  delta,
  hint,
  tone = "default",
}: {
  label: string;
  value: string;
  delta?: number;
  hint?: string;
  tone?: "default" | "positive" | "warning" | "negative";
}) {
  return (
    <div className="panel relative overflow-hidden px-4 py-3">
      <span
        className={cn(
          "absolute inset-x-0 top-0 h-px",
          tone === "default" && "bg-primary/50",
          tone === "positive" && "bg-positive/60",
          tone === "warning" && "bg-warning/60",
          tone === "negative" && "bg-negative/60",
        )}
      />
      <p className="label-caps">{label}</p>
      <div className="mt-1.5 flex flex-wrap items-baseline gap-x-2 gap-y-1">
        <span className="tabular text-2xl leading-none font-semibold whitespace-nowrap text-foreground">
          {value}
        </span>
        {delta != null && <Delta value={delta} />}
      </div>
      {hint && <p className="mt-1.5 text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

/* ------------------------------ Meters ------------------------------- */
export function ScoreBar({
  value,
  max = 100,
  tone = "primary",
}: {
  value: number;
  max?: number;
  tone?: "primary" | "positive" | "warning" | "negative";
}) {
  const width = Math.max(2, Math.min(100, (value / max) * 100));
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-14 overflow-hidden rounded-full bg-muted">
        <div
          className={cn(
            "h-full rounded-full",
            tone === "primary" && "bg-primary",
            tone === "positive" && "bg-positive",
            tone === "warning" && "bg-warning",
            tone === "negative" && "bg-negative",
          )}
          style={{ width: `${width}%` }}
        />
      </div>
      <span className="tabular text-xs text-foreground">{value}</span>
    </div>
  );
}

export function ScoutScore({ value }: { value: number }) {
  const tone = value >= 78 ? "positive" : value >= 60 ? "primary" : value >= 45 ? "warning" : "negative";
  return <ScoreBar value={value} tone={tone} />;
}

export function DifficultyPips({ value }: { value: number }) {
  return (
    <span className="inline-flex items-center gap-0.5" aria-label={`Difficulty ${value} of 5`}>
      {[1, 2, 3, 4, 5].map((i) => (
        <span
          key={i}
          className={cn(
            "h-3 w-1 rounded-sm",
            i <= value
              ? value >= 4
                ? "bg-negative"
                : value === 3
                  ? "bg-warning"
                  : "bg-positive"
              : "bg-muted",
          )}
        />
      ))}
    </span>
  );
}

/* --------------------------- State surfaces -------------------------- */
export function EmptyState({
  title,
  description,
  action,
  icon: Icon = Inbox,
}: {
  title: string;
  description: string;
  action?: ReactNode;
  icon?: typeof Inbox;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="grid size-11 place-items-center rounded-lg border border-border bg-elevated">
        <Icon className="size-5 text-muted-foreground" />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-foreground">{title}</h3>
      <p className="mt-1 max-w-sm text-xs text-muted-foreground">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="grid size-11 place-items-center rounded-lg border border-negative/40 bg-negative/10">
        <TriangleAlert className="size-5 text-negative" />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-foreground">Data unavailable</h3>
      <p className="mt-1 max-w-sm text-xs text-muted-foreground">
        {message ?? "The intelligence feed didn't respond. Retry in a moment."}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 rounded-md border border-border-strong bg-elevated px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-accent"
        >
          Retry
        </button>
      )}
    </div>
  );
}

export function TableSkeleton({ rows = 8, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className="divide-y divide-border">
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex items-center gap-4 px-4 py-2.5">
          {Array.from({ length: cols }).map((_, c) => (
            <Skeleton
              key={c}
              className="h-3.5 bg-muted"
              style={{ width: c === 0 ? "22%" : `${Math.max(6, 70 / cols)}%` }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export function KpiSkeleton({ count = 6 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="panel px-4 py-3">
          <Skeleton className="h-2.5 w-20 bg-muted" />
          <Skeleton className="mt-3 h-6 w-24 bg-muted" />
          <Skeleton className="mt-3 h-2.5 w-28 bg-muted" />
        </div>
      ))}
    </>
  );
}
