import { cn } from "@/lib/utils";
import type { Player, Position } from "@/types";

const posTone: Record<Position, string> = {
  GK: "border-warning/40 bg-warning/12 text-warning",
  DEF: "border-primary/40 bg-primary/12 text-primary",
  MID: "border-positive/40 bg-positive/12 text-positive",
  FWD: "border-chart-5/40 bg-chart-5/12 text-chart-5",
};

export function PositionTag({ value }: { value: Position }) {
  return (
    <span
      className={cn(
        "inline-flex w-9 justify-center rounded-sm border px-1 py-0.5 text-[10.5px] font-semibold tracking-wide",
        posTone[value],
      )}
    >
      {value}
    </span>
  );
}

export function initials(name: string) {
  return name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("");
}

export function PlayerIdentity({
  player,
  size = "sm",
}: {
  player: Pick<Player, "name" | "club" | "position" | "photoUrl">;
  size?: "sm" | "lg";
}) {
  return (
    <div className="flex items-center gap-2.5">
      <div
        className={cn(
          "grid shrink-0 place-items-center overflow-hidden rounded-md border border-border bg-elevated font-semibold text-muted-foreground",
          size === "sm" ? "size-7 text-[11px]" : "size-10 text-sm",
        )}
      >
        {player.photoUrl ? (
          <img src={player.photoUrl} alt={player.name} className="h-full w-full object-cover" />
        ) : (
          initials(player.name)
        )}
      </div>
      <div className="min-w-0">
        <div className="truncate text-sm leading-tight font-medium text-foreground">
          {player.name}
        </div>
        <div className="truncate text-[11px] leading-tight text-muted-foreground">
          {player.club}
        </div>
      </div>
    </div>
  );
}
