import type {
  Alert,
  Card,
  Club,
  DashboardKpis,
  DataFreshness,
  Fixture,
  Gameweek,
  GroupMember,
  MarketData,
  MarketOverview,
  NewsArticle,
  Paginated,
  Player,
  PlayerFixture,
  PortfolioSummary,
  ScoutFilters,
  WatchlistEntry,
} from "@/types";

export interface ScoutQuery extends ScoutFilters {
  page?: number;
  pageSize?: number;
  sortBy?: keyof Player;
  sortDir?: "asc" | "desc";
}

/** The single contract the UI depends on — mock and REST both implement it. */
export interface ScoutlabApi {
  getDataFreshness(): Promise<DataFreshness>;
  getGameweeks(): Promise<Gameweek[]>;
  getClubs(): Promise<Club[]>;
  getCompetitions(): Promise<string[]>;

  getDashboardKpis(): Promise<DashboardKpis>;
  getScoutingOpportunities(limit?: number): Promise<Player[]>;

  searchPlayers(query: ScoutQuery): Promise<Paginated<Player>>;
  getPlayer(id: string): Promise<Player>;
  getPlayerMarket(id: string): Promise<MarketData>;
  getPlayerFixtures(id: string): Promise<PlayerFixture[]>;

  getMarketOverview(): Promise<MarketOverview>;
  getFixtures(filters?: {
    gameweek?: number | undefined;
    competition?: string | undefined;
    clubId?: string | undefined;
  }): Promise<Fixture[]>;

  getMyCards(): Promise<Card[]>;
  getPortfolioSummary(): Promise<PortfolioSummary>;

  getWatchlist(): Promise<WatchlistEntry[]>;
  addToWatchlist(playerId: string): Promise<WatchlistEntry[]>;
  removeFromWatchlist(playerId: string): Promise<WatchlistEntry[]>;

  getNews(filters?: { category?: string | undefined }): Promise<NewsArticle[]>;
  getGroupMembers(): Promise<GroupMember[]>;
  getAlerts(): Promise<Alert[]>;
  markAlertRead(id: string): Promise<Alert[]>;
  markAllAlertsRead(): Promise<Alert[]>;
}
