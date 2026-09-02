import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { PageHeader } from "@/components/layout/AppShell";
import { Panel, Tag } from "@/components/scoutlab/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { freshnessQuery } from "@/services/queries";
import { dateTime } from "@/lib/format";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — Preferences & Data Sources | ScoutLab" },
      {
        name: "description",
        content:
          "Configure ScoutLab display preferences, alert thresholds, scouting model weights and data source status.",
      },
      { property: "og:title", content: "Settings — Preferences & Data Sources | ScoutLab" },
      {
        property: "og:description",
        content: "Manage alert thresholds, default filters and data refresh behaviour.",
      },
    ],
  }),
  component: SettingsPage,
});

function Row({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
      <div className="min-w-0">
        <p className="text-xs font-medium text-foreground">{label}</p>
        {hint && <p className="mt-0.5 text-[11px] text-muted-foreground">{hint}</p>}
      </div>
      {children}
    </div>
  );
}

function SettingsPage() {
  const freshness = useQuery(freshnessQuery);

  return (
    <>
      <PageHeader
        title="Settings"
        description="Preferences, alert thresholds and data source status"
        actions={
          <Button size="sm" className="h-8 text-xs" onClick={() => toast.success("Preferences saved")}>
            Save changes
          </Button>
        }
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Display" bodyClassName="divide-y divide-border">
          <Row label="Currency" hint="Used for all market values">
            <Select defaultValue="eth">
              <SelectTrigger className="h-8 w-28 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="eth">ETH</SelectItem>
                <SelectItem value="eur">EUR</SelectItem>
                <SelectItem value="usd">USD</SelectItem>
              </SelectContent>
            </Select>
          </Row>
          <Row label="Default landing page">
            <Select defaultValue="dashboard">
              <SelectTrigger className="h-8 w-32 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dashboard">Dashboard</SelectItem>
                <SelectItem value="scout">Scout</SelectItem>
                <SelectItem value="market">Market</SelectItem>
              </SelectContent>
            </Select>
          </Row>
          <Row label="Compact tables" hint="Denser rows for large screens">
            <Switch defaultChecked />
          </Row>
        </Panel>

        <Panel title="Alerts" bodyClassName="divide-y divide-border">
          <Row label="Price move threshold" hint="Trigger an alert beyond this 24h move">
            <Input defaultValue="8" className="h-8 w-20 text-xs" />
          </Row>
          <Row label="Starting XI change" hint="Alert when probability shifts by 15 points">
            <Switch defaultChecked />
          </Row>
          <Row label="Injury and suspension news">
            <Switch defaultChecked />
          </Row>
          <Row label="Fixture difficulty revisions">
            <Switch />
          </Row>
        </Panel>

        <Panel title="Scouting model" bodyClassName="divide-y divide-border">
          <Row label="Model version" hint="Scout Score weighting profile">
            <Tag tone="primary">v2.4 balanced</Tag>
          </Row>
          <Row label="Risk tolerance">
            <Select defaultValue="balanced">
              <SelectTrigger className="h-8 w-32 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="conservative">Conservative</SelectItem>
                <SelectItem value="balanced">Balanced</SelectItem>
                <SelectItem value="aggressive">Aggressive</SelectItem>
              </SelectContent>
            </Select>
          </Row>
          <Row label="Exclude unavailable players by default">
            <Switch defaultChecked />
          </Row>
        </Panel>

        <Panel title="Data sources" bodyClassName="divide-y divide-border">
          <Row label="Market feed" hint="Card prices, listings and sales">
            <Tag tone="positive">Connected</Tag>
          </Row>
          <Row label="Performance & scores" hint="Gameweek scoring data">
            <Tag tone="positive">Connected</Tag>
          </Row>
          <Row label="Availability feed" hint="Injuries, suspensions, line-up reports">
            <Tag tone="warning">Partial coverage</Tag>
          </Row>
          <Row
            label="Last synchronisation"
            hint={freshness.data ? dateTime(freshness.data.lastUpdated) : "Syncing…"}
          >
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs"
              onClick={() => void freshness.refetch()}
            >
              Sync now
            </Button>
          </Row>
          <Row
            label="Backend"
            hint="Currently served by the ScoutLab mock service; REST endpoints slot in behind the same interface."
          >
            <Tag tone="muted">Mock data</Tag>
          </Row>
        </Panel>
      </div>
    </>
  );
}
