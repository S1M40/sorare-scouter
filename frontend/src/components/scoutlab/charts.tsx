import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const axis = {
  stroke: "var(--color-border-strong)",
  tick: { fill: "var(--color-muted-foreground)", fontSize: 10 },
};

const tooltipStyle = {
  contentStyle: {
    background: "var(--color-popover)",
    border: "1px solid var(--color-border-strong)",
    borderRadius: 6,
    fontSize: 11,
    padding: "6px 8px",
  },
  labelStyle: { color: "var(--color-muted-foreground)", fontSize: 10 },
  itemStyle: { color: "var(--color-foreground)" },
};

export function AreaTrend({
  data,
  xKey,
  yKey,
  color = "var(--color-primary)",
  height = 180,
}: {
  data: Record<string, unknown>[];
  xKey: string;
  yKey: string;
  color?: string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={`fill-${yKey}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="var(--color-border)" vertical={false} />
        <XAxis dataKey={xKey} {...axis} tickLine={false} minTickGap={28} />
        <YAxis {...axis} tickLine={false} width={38} />
        <Tooltip {...tooltipStyle} />
        <Area
          type="monotone"
          dataKey={yKey}
          stroke={color}
          strokeWidth={1.6}
          fill={`url(#fill-${yKey})`}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function MultiLine({
  data,
  xKey,
  series,
  height = 200,
}: {
  data: Record<string, unknown>[];
  xKey: string;
  series: { key: string; color: string; dashed?: boolean; name?: string }[];
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="var(--color-border)" vertical={false} />
        <XAxis dataKey={xKey} {...axis} tickLine={false} minTickGap={20} />
        <YAxis {...axis} tickLine={false} width={34} />
        <Tooltip {...tooltipStyle} />
        {series.map((s) => (
          <Line
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.name ?? s.key}
            stroke={s.color}
            strokeWidth={1.7}
            strokeDasharray={s.dashed ? "4 3" : undefined}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function Bars({
  data,
  xKey,
  yKey,
  color = "var(--color-primary)",
  height = 180,
}: {
  data: Record<string, unknown>[];
  xKey: string;
  yKey: string;
  color?: string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="var(--color-border)" vertical={false} />
        <XAxis dataKey={xKey} {...axis} tickLine={false} />
        <YAxis {...axis} tickLine={false} width={34} />
        <Tooltip {...tooltipStyle} />
        <Bar dataKey={yKey} fill={color} radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function Sparkline({
  data,
  yKey,
  positive,
}: {
  data: Record<string, unknown>[];
  yKey: string;
  positive: boolean;
}) {
  return (
    <ResponsiveContainer width="100%" height={28}>
      <LineChart data={data}>
        <Line
          type="monotone"
          dataKey={yKey}
          stroke={positive ? "var(--color-positive)" : "var(--color-negative)"}
          strokeWidth={1.4}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
