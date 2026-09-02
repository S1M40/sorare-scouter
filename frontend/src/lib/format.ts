export const eth = (n: number, d = 2) => `${n.toFixed(d)} Ξ`;
export const pct = (n: number, d = 0) => `${n.toFixed(d)}%`;
export const signedPct = (n: number, d = 1) => `${n > 0 ? "+" : ""}${n.toFixed(d)}%`;
export const signed = (n: number, d = 2) => `${n > 0 ? "+" : ""}${n.toFixed(d)}`;

export function relativeTime(isoDate: string, now = new Date()): string {
  const diff = now.getTime() - new Date(isoDate).getTime();
  const mins = Math.round(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  if (days < 30) return `${days}d ago`;
  return `${Math.round(days / 30)}mo ago`;
}

export function shortDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
}

export function dateTime(isoDate: string): string {
  return new Date(isoDate).toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export const toneForDelta = (n: number) =>
  n > 0 ? "text-positive" : n < 0 ? "text-negative" : "text-muted-foreground";
