import { queryOptions } from "@tanstack/react-query";
import { api } from "@/services/api";
import type { ScoutQuery } from "@/services/api/types";

export const qk = {
  freshness: ["freshness"] as const,
  clubs: ["clubs"] as const,
  competitions: ["competitions"] as const,
  gameweeks: ["gameweeks"] as const,
  kpis: ["kpis"] as const,
  opportunities: ["opportunities"] as const,
  scout: (q: ScoutQuery) => ["scout", q] as const,
  player: (id: string) => ["player", id] as const,
  playerMarket: (id: string) => ["player-market", id] as const,
  playerFixtures: (id: string) => ["player-fixtures", id] as const,
  market: ["market-overview"] as const,
  fixtures: (f: {
    gameweek?: number | undefined;
    competition?: string | undefined;
    clubId?: string | undefined;
  }) =>
    ["fixtures", f] as const,
  cards: ["cards"] as const,
  portfolio: ["portfolio"] as const,
  watchlist: ["watchlist"] as const,
  news: (category?: string) => ["news", category ?? "all"] as const,
  group: ["group"] as const,
  alerts: ["alerts"] as const,
};

export const freshnessQuery = queryOptions({
  queryKey: qk.freshness,
  queryFn: () => api.getDataFreshness(),
});
export const clubsQuery = queryOptions({ queryKey: qk.clubs, queryFn: () => api.getClubs() });
export const competitionsQuery = queryOptions({
  queryKey: qk.competitions,
  queryFn: () => api.getCompetitions(),
});
export const gameweeksQuery = queryOptions({
  queryKey: qk.gameweeks,
  queryFn: () => api.getGameweeks(),
});
export const kpisQuery = queryOptions({ queryKey: qk.kpis, queryFn: () => api.getDashboardKpis() });
export const opportunitiesQuery = queryOptions({
  queryKey: qk.opportunities,
  queryFn: () => api.getScoutingOpportunities(12),
});
export const scoutQuery = (q: ScoutQuery) =>
  queryOptions({ queryKey: qk.scout(q), queryFn: () => api.searchPlayers(q) });
export const playerQuery = (id: string) =>
  queryOptions({ queryKey: qk.player(id), queryFn: () => api.getPlayer(id) });
export const playerMarketQuery = (id: string) =>
  queryOptions({ queryKey: qk.playerMarket(id), queryFn: () => api.getPlayerMarket(id) });
export const playerFixturesQuery = (id: string) =>
  queryOptions({ queryKey: qk.playerFixtures(id), queryFn: () => api.getPlayerFixtures(id) });
export const marketQuery = queryOptions({
  queryKey: qk.market,
  queryFn: () => api.getMarketOverview(),
});
export const fixturesQuery = (f: {
  gameweek?: number | undefined;
  competition?: string | undefined;
  clubId?: string | undefined;
}) =>
  queryOptions({ queryKey: qk.fixtures(f), queryFn: () => api.getFixtures(f) });
export const cardsQuery = queryOptions({ queryKey: qk.cards, queryFn: () => api.getMyCards() });
export const portfolioQuery = queryOptions({
  queryKey: qk.portfolio,
  queryFn: () => api.getPortfolioSummary(),
});
export const watchlistQuery = queryOptions({
  queryKey: qk.watchlist,
  queryFn: () => api.getWatchlist(),
});
export const newsQuery = (category?: string | undefined) =>
  queryOptions({ queryKey: qk.news(category), queryFn: () => api.getNews({ category }) });
export const groupQuery = queryOptions({ queryKey: qk.group, queryFn: () => api.getGroupMembers() });
export const alertsQuery = queryOptions({ queryKey: qk.alerts, queryFn: () => api.getAlerts() });
