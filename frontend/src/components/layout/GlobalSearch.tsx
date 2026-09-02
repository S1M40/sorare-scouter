import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { scoutQuery } from "@/services/queries";
import { navItems } from "./nav";
import { PositionTag } from "@/components/scoutlab/PlayerIdentity";
import { eth } from "@/lib/format";

export function GlobalSearch() {
  const [open, setOpen] = useState(false);
  const [term, setTerm] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const { data } = useQuery({
    ...scoutQuery({ search: term, pageSize: 7 }),
    enabled: open && term.length > 1,
  });

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex h-8 w-full max-w-sm items-center gap-2 rounded-md border border-border bg-elevated px-2.5 text-xs text-muted-foreground transition-colors hover:border-border-strong"
      >
        <Search className="size-3.5" />
        <span className="truncate">Search players, clubs, competitions…</span>
        <kbd className="tabular ml-auto hidden rounded border border-border-strong px-1 py-px text-[10px] sm:block">
          ⌘K
        </kbd>
      </button>

      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput
          placeholder="Search players or jump to a page…"
          value={term}
          onValueChange={setTerm}
        />
        <CommandList>
          <CommandEmpty>No matches found.</CommandEmpty>
          {!!data?.items.length && (
            <CommandGroup heading="Players">
              {data.items.map((p) => (
                <CommandItem
                  key={p.id}
                  value={`${p.name} ${p.club}`}
                  onSelect={() => {
                    setOpen(false);
                    void navigate({ to: "/players/$playerId", params: { playerId: p.id } });
                  }}
                  className="gap-2"
                >
                  <PositionTag value={p.position} />
                  <span className="text-foreground">{p.name}</span>
                  <span className="text-muted-foreground">· {p.club}</span>
                  <span className="tabular ml-auto text-xs text-muted-foreground">
                    {eth(p.marketPrice)}
                  </span>
                </CommandItem>
              ))}
            </CommandGroup>
          )}
          <CommandGroup heading="Navigate">
            {navItems.map((item) => (
              <CommandItem
                key={item.to}
                value={item.label}
                onSelect={() => {
                  setOpen(false);
                  void navigate({ to: item.to });
                }}
                className="gap-2"
              >
                <item.icon className="size-3.5 text-muted-foreground" />
                {item.label}
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}
