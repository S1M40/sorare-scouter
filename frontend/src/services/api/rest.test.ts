import { describe, it, expect, vi } from "vitest";
import { createRestApi } from "./rest";

describe("REST Adapter", () => {
  it("getDataFreshness unwraps envelope and maps Gameweek correctly", async () => {
    const mockHttp = vi.fn().mockResolvedValue({
      data: {
        current_gameweek: {
          game_week: 100,
          event_name: "GW 100",
          state: "live",
          start_date: "2024-01-01T00:00:00Z",
          end_date: "2024-01-04T00:00:00Z",
        },
        data_freshness: {
          last_sync_at: "2024-01-02T00:00:00Z",
          status: "fresh",
        },
      },
      meta: { source: "scoutlab" },
    });

    const api = createRestApi(mockHttp);
    const result = await api.getDataFreshness();

    expect(mockHttp).toHaveBeenCalledWith("/api/v1/dashboard");
    expect(result.status).toBe("FRESH");
    expect(result.gameweek.id).toBe(100);
    expect(result.gameweek.status).toBe("LIVE");
  });

  it("searchPlayers maps parameters and transforms response", async () => {
    const mockHttp = vi.fn().mockResolvedValue({
      data: [
        {
          id: 1,
          display_name: "Test Player",
          age: 25,
          position: "Forward",
          club: { name: "Test Club", competition: { name: "Test League" } },
          is_injured: true,
          scout_score: 85,
        },
      ],
      meta: { total: 1, page: 1, page_size: 25 },
    });

    const api = createRestApi(mockHttp);
    const result = await api.searchPlayers({
      search: "Test",
      positions: ["FWD"],
      sortBy: "scoutScore",
    });

    // Check query params were built correctly
    const callUrl = mockHttp.mock.calls[0][0];
    expect(callUrl).toContain("search=Test");
    expect(callUrl).toContain("position=Forward");
    expect(callUrl).toContain("sort_by=scout_score");

    // Check mapping
    expect(result.total).toBe(1);
    expect(result.items[0].id).toBe("1");
    expect(result.items[0].name).toBe("Test Player");
    expect(result.items[0].position).toBe("FWD");
    expect(result.items[0].club).toBe("Test Club");
    expect(result.items[0].availability).toBe("INJURED");
  });
});

