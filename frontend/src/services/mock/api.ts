import { latency } from "@/services/api/client";
import type { ScoutQuery, ScoutlabApi } from "@/services/api/types";
import type { Alert, Player, WatchlistEntry } from "@/types";
import {
  alerts as seedAlerts,
  cards,
  clubs,
  competitions,
  computeKpis,
  computeMarketOverview,
  computeFreshness,
  fixtures,
  gameweeks,
  groupMembers,
  marketByPlayer,
  news,
  playerFixtures,
  players,
  playersById,
  watchlist as seedWatchlist,
} from "./data";

/* Mutable in-memory session state — replaced by real endpoints later. */
let alertState: Alert[] = seedAlerts.map((a) => ({ ...a }));
let watchlistState: WatchlistEntry[] = seedWatchlist.map((w) => ({ ...w }));

function matches(p: Player, q: ScoutQuery): boolean {
  if (q.search) {
    const s = q.search.toLowerCase();
    if (!p.name.toLowerCase().includes(s) && !p.club.toLowerCase().includes(s)) return false;
  }
  if (q.positions?.length && !q.positions.includes(p.position)) return false;
  if (q.clubs?.length && !q.clubs.includes(p.club)) return false;
  if (q.competitions?.length && !q.competitions.includes(p.competition)) return false;
  if (q.ageMax != null && p.age > q.ageMax) return false;
  if (q.priceMax != null && p.marketPrice > q.priceMax) return false;
  if (q.minAverageScore != null && p.averageScore < q.minAverageScore) return false;
  if (q.minForm != null && p.form < q.minForm) return false;
  if (q.minProjected != null && p.projectedScore < q.minProjected) return false;
  if (q.minStartingProbability != null && p.startingProbability < q.minStartingProbability)
    return false;
  if (q.minMinutesShare != null && p.minutesShare < q.minMinutesShare) return false;
  if (q.excludeInjured && (p.availability === "INJURED" || p.availability === "DOUBTFUL"))
    return false;
  if (q.excludeSuspended && p.suspension.suspended) return false;
  if (q.minScoutScore != null && p.scoutScore < q.minScoutScore) return false;
  if (q.risk?.length && !q.risk.includes(p.risk)) return false;
  if (q.recommendations?.length && !q.recommendations.includes(p.recommendation)) return false;
  return true;
}

export const mockApi: ScoutlabApi = {
  getDataFreshness: () => latency(computeFreshness(), 120),
  getGameweeks: () => latency(gameweeks, 120),
  getClubs: () => latency(clubs, 120),
  getCompetitions: () => latency(competitions, 120),

  getDashboardKpis: () => latency(computeKpis()),
  getScoutingOpportunities: (limit = 12) =>
    latency(
      [...players]
        .filter((p) => p.availability === "AVAILABLE")
        .sort((a, b) => b.scoutScore - a.scoutScore)
        .slice(0, limit),
    ),

  searchPlayers: (query) => {
    const { page = 1, pageSize = 25, sortBy = "scoutScore", sortDir = "desc" } = query;
    const filtered = players.filter((p) => matches(p, query));
    const sorted = [...filtered].sort((a, b) => {
      const av = a[sortBy];
      const bv = b[sortBy];
      if (typeof av === "number" && typeof bv === "number")
        return sortDir === "asc" ? av - bv : bv - av;
      return sortDir === "asc"
        ? String(av).localeCompare(String(bv))
        : String(bv).localeCompare(String(av));
    });
    return latency({
      items: sorted.slice((page - 1) * pageSize, page * pageSize),
      total: sorted.length,
      page,
      pageSize,
    });
  },

  getPlayer: (id) => {
    const player = playersById.get(id);
    if (!player) return Promise.reject(new Error(`Player not found: ${id}`));
    return latency(player);
  },
  getPlayerMarket: (id) => {
    const market = marketByPlayer.get(id);
    if (!market) return Promise.reject(new Error(`No market data for ${id}`));
    return latency(market);
  },
  getPlayerFixtures: (id) => {
    const player = playersById.get(id);
    if (!player) return Promise.reject(new Error(`Player not found: ${id}`));
    return latency(playerFixtures(player));
  },

  getMarketOverview: () => latency(computeMarketOverview()),
  getFixtures: (filters) =>
    latency(
      fixtures.filter(
        (f) =>
          (filters?.gameweek == null || f.gameweek === filters.gameweek) &&
          (!filters?.competition || f.competition === filters.competition) &&
          (!filters?.clubId || f.homeClubId === filters.clubId || f.awayClubId === filters.clubId),
      ),
    ),

  getMyCards: () => latency(cards),
  getPortfolioSummary: () => {
    const totalValue = cards.reduce((s, c) => s + c.price, 0);
    const acquired = cards.reduce((s, c) => s + c.acquiredPrice, 0);
    return latency({
      totalValue: Number(totalValue.toFixed(2)),
      change7d: Number((totalValue - acquired).toFixed(2)),
      changePct7d: Number((((totalValue - acquired) / acquired) * 100).toFixed(1)),
      averageScore: Math.round(cards.reduce((s, c) => s + c.player.averageScore, 0) / cards.length),
      cardCount: cards.length,
      atRisk: cards.filter((c) => c.player.availability !== "AVAILABLE").length,
    });
  },

  getWatchlist: () => latency(watchlistState),
  addToWatchlist: (playerId) => {
    const player = playersById.get(playerId);
    if (player && !watchlistState.some((w) => w.playerId === playerId)) {
      watchlistState = [
        {
          id: `wl-${playerId}`,
          playerId,
          player,
          addedAt: new Date().toISOString(),
          targetPrice: Number((player.marketPrice * 0.85).toFixed(2)),
          latestAlert: undefined,
        },
        ...watchlistState,
      ];
    }
    return latency(watchlistState, 140);
  },
  removeFromWatchlist: (playerId) => {
    watchlistState = watchlistState.filter((w) => w.playerId !== playerId);
    return latency(watchlistState, 140);
  },

  getNews: (filters) =>
    latency(news.filter((n) => !filters?.category || n.category === filters.category)),
  getGroupMembers: () => latency(groupMembers),

  getAlerts: () => latency(alertState),
  markAlertRead: (id) => {
    alertState = alertState.map((a) => (a.id === id ? { ...a, read: true } : a));
    return latency(alertState, 100);
  },
  markAllAlertsRead: () => {
    alertState = alertState.map((a) => ({ ...a, read: true }));
    return latency(alertState, 100);
  },
};
