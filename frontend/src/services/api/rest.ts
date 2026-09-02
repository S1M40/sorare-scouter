/**
 * REST adapter — bridges the FastAPI backend to the frontend ScoutlabApi interface.
 *
 * Responsibilities:
 * 1. Unwraps the `ApiResponse { data, meta }` envelope
 * 2. Converts `snake_case` keys → `camelCase`
 * 3. Maps enum values (Position, Severity, Rarity, etc.)
 * 4. Coerces `int` IDs → `string`
 * 5. Reshapes flat backend schemas into nested frontend types
 *
 * No component or page changes are required — this file is the only integration layer.
 */

import type { http as HttpFn } from "./client";
import type { ScoutlabApi, ScoutQuery } from "./types";
import type {
  Alert,
  AlertCategory,
  AvailabilityStatus,
  Card,
  Club,
  DashboardKpis,
  DataFreshness,
  Fixture,
  Gameweek,
  GroupMember,
  InjuryInfo,
  MarketData,
  MarketOverview,
  NewsArticle,
  Paginated,
  Player,
  PlayerFixture,
  PlayerScore,
  PortfolioSummary,
  Position,
  PricePoint,
  Rarity,
  Recommendation,
  RiskLevel,
  ScoutingAnalysis,
  SuspensionInfo,
  WatchlistEntry,
} from "@/types";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Extract `.data` from the backend's `ApiResponse` / `ApiListResponse` envelope. */
function unwrap<T>(response: { data: T; meta?: unknown }): T {
  return response.data;
}

/** Recursively transform object keys from snake_case to camelCase. */
function snakeToCamel(obj: unknown): unknown {
  if (obj === null || obj === undefined) return obj;
  if (Array.isArray(obj)) return obj.map(snakeToCamel);
  if (typeof obj === "object" && !(obj instanceof Date)) {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj as Record<string, unknown>)) {
      const camelKey = key.replace(/_([a-z0-9])/g, (_, c) => (c as string).toUpperCase());
      result[camelKey] = snakeToCamel(value);
    }
    return result;
  }
  return obj;
}

/** Safely stringify an id (backend returns int, frontend expects string). */
function sid(id: number | string | undefined | null): string {
  return String(id ?? "");
}

// ---------------------------------------------------------------------------
// Enum mappers
// ---------------------------------------------------------------------------

const POSITION_MAP: Record<string, Position> = {
  Goalkeeper: "GK",
  Defender: "DEF",
  Midfielder: "MID",
  Forward: "FWD",
  // Passthrough for already-short values
  GK: "GK",
  DEF: "DEF",
  MID: "MID",
  FWD: "FWD",
};

function mapPosition(raw: string): Position {
  return POSITION_MAP[raw] ?? "MID";
}

const SEVERITY_MAP: Record<string, Alert["severity"]> = {
  INFO: "info",
  WARNING: "warning",
  CRITICAL: "negative",
  SUCCESS: "positive",
};

function mapSeverity(raw: string): Alert["severity"] {
  return SEVERITY_MAP[raw] ?? "info";
}

const ALERT_TYPE_MAP: Record<string, AlertCategory> = {
  injury: "Injury",
  suspension: "Suspension",
  price: "Price",
  starting_xi: "Starting XI",
  fixture: "Fixture",
  performance: "Performance",
  Injury: "Injury",
  Suspension: "Suspension",
  Price: "Price",
  "Starting XI": "Starting XI",
  Fixture: "Fixture",
  Performance: "Performance",
};

function mapAlertCategory(raw: string): AlertCategory {
  return ALERT_TYPE_MAP[raw] ?? ("Performance" as AlertCategory);
}

function mapRiskLevel(raw: string | null | undefined): RiskLevel {
  if (raw === "CRITICAL") return "HIGH"; // Frontend has no CRITICAL
  if (raw === "LOW" || raw === "MEDIUM" || raw === "HIGH") return raw;
  return "LOW";
}

function mapRarity(raw: string | null | undefined): Rarity {
  if (raw === "super_rare") return "super rare";
  if (raw === "limited" || raw === "rare" || raw === "unique") return raw;
  return "common";
}

function mapAvailability(isInjured: boolean, isSuspended: boolean): AvailabilityStatus {
  if (isSuspended) return "SUSPENDED";
  if (isInjured) return "INJURED";
  return "AVAILABLE";
}

function mapRecommendation(raw: string | null | undefined): Recommendation {
  const valid = ["BUY", "WATCH", "HOLD", "SELL", "AVOID"] as const;
  if (raw && valid.includes(raw as Recommendation)) return raw as Recommendation;
  return "HOLD";
}

// ---------------------------------------------------------------------------
// Entity mappers: Backend → Frontend
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapPlayer(raw: any): Player {
  const club = raw.club;
  const metric = raw.metric;
  const injuries: unknown[] = raw.active_injuries ?? raw.activeInjuries ?? [];
  const suspensions: unknown[] = raw.active_suspensions ?? raw.activeSuspensions ?? [];
  const scores: unknown[] = raw.recent_scores ?? raw.recentScores ?? [];

  // Build InjuryInfo from first active injury or defaults
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const firstInjury = injuries.find((i: any) => i.active) as any;
  const injury: InjuryInfo = firstInjury
    ? {
        status: firstInjury.status ?? (raw.is_injured || raw.isInjured ? "INJURED" : "AVAILABLE"),
        description: firstInjury.details ?? firstInjury.kind ?? undefined,
        expectedReturn: firstInjury.expected_end_date ?? firstInjury.expectedEndDate ?? undefined,
        provenance: firstInjury.source_type ?? firstInjury.sourceType ?? "FACT",
        source: undefined,
        updatedAt: firstInjury.start_date ?? firstInjury.startDate ?? new Date().toISOString(),
      }
    : {
        status: (raw.is_injured || raw.isInjured) ? "INJURED" : "AVAILABLE",
        provenance: "FACT" as const,
        updatedAt: new Date().toISOString(),
      };

  // Build SuspensionInfo
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const firstSusp = suspensions.find((s: any) => s.active) as any;
  const suspension: SuspensionInfo = firstSusp
    ? {
        suspended: true,
        reason: firstSusp.reason ?? firstSusp.kind ?? undefined,
        matchesRemaining: firstSusp.matches ?? undefined,
        provenance: firstSusp.source_type ?? firstSusp.sourceType ?? "FACT",
      }
    : {
        suspended: raw.is_suspended ?? raw.isSuspended ?? false,
        provenance: "FACT" as const,
      };

  // Map scores
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mappedScores: PlayerScore[] = scores.map((s: any) => ({
    gameweek: s.game_id ?? s.gameId ?? 0,
    date: s.created_at ?? s.createdAt ?? new Date().toISOString(),
    opponent: "",
    score: s.score ?? 0,
    projected: s.projected_score ?? s.projectedScore ?? 0,
    minutes: 90,
    decisiveScore: s.decisive_score ?? s.decisiveScore ?? 0,
    allAroundScore: s.all_around_score ?? s.allAroundScore ?? 0,
  }));

  // Build ScoutingAnalysis from metric
  const analysis: ScoutingAnalysis = metric?.recommendation_detail ?? metric?.recommendationDetail
    ? {
        strengths: (metric.recommendation_detail ?? metric.recommendationDetail)?.reasons ?? [],
        weaknesses: (metric.recommendation_detail ?? metric.recommendationDetail)?.risks ?? [],
        opportunity: `Scout Score: ${metric.scout_score ?? metric.scoutScore ?? 0}`,
        riskFactors: (metric.risk_factors ?? metric.riskFactors ?? [])
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .map((rf: any) => rf.message),
        scoutScoreExplanation: `Form ${metric.form_score ?? metric.formScore ?? 0} | Consistency ${metric.consistency_score ?? metric.consistencyScore ?? 0} | Minutes ${metric.minutes_score ?? metric.minutesScore ?? 0} | Fixture ${metric.fixture_score ?? metric.fixtureScore ?? 0} | Availability ${metric.availability_score ?? metric.availabilityScore ?? 0} | Market ${metric.market_score ?? metric.marketScore ?? 0}`,
        confidence: (metric.confidence ?? 50) >= 70 ? "HIGH" : (metric.confidence ?? 50) >= 40 ? "MEDIUM" : "LOW",
      }
    : {
        strengths: [],
        weaknesses: [],
        opportunity: "",
        riskFactors: [],
        scoutScoreExplanation: "",
        confidence: "MEDIUM" as const,
      };

  const clubName = typeof club === "string" ? club : club?.name ?? "";
  const clubId = typeof club === "string" ? "" : sid(club?.id);
  const competitionName = typeof club === "object" && club !== null
    ? (club.competition?.name ?? club.competition ?? "")
    : "";

  return {
    id: sid(raw.id),
    name: raw.display_name ?? raw.displayName ?? `${raw.first_name ?? raw.firstName ?? ""} ${raw.last_name ?? raw.lastName ?? ""}`.trim(),
    age: raw.age ?? 0,
    position: mapPosition(raw.position ?? "Midfielder"),
    clubId,
    club: clubName,
    competition: competitionName,
    nationality: raw.nationality ?? "",
    photoUrl: raw.image_url ?? raw.imageUrl ?? undefined,
    averageScore: metric?.form_score ?? metric?.formScore ?? raw.form_score ?? raw.formScore ?? 0,
    form: metric?.form_score ?? metric?.formScore ?? raw.form_score ?? raw.formScore ?? 0,
    projectedScore: metric?.scout_score ?? metric?.scoutScore ?? raw.scout_score ?? raw.scoutScore ?? 0,
    startingProbability: metric?.starting_probability ?? metric?.startingProbability ?? raw.starting_probability ?? raw.startingProbability ?? 50,
    minutesShare: metric?.minutes_score ?? metric?.minutesScore ?? 50,
    consistency: metric?.consistency_score ?? metric?.consistencyScore ?? 50,
    ceiling: (metric?.form_score ?? metric?.formScore ?? 50) + 15,
    floor: Math.max(0, (metric?.form_score ?? metric?.formScore ?? 50) - 15),
    scoutScore: metric?.scout_score ?? metric?.scoutScore ?? raw.scout_score ?? raw.scoutScore ?? 0,
    risk: mapRiskLevel(metric?.risk_level ?? metric?.riskLevel ?? raw.risk_level ?? raw.riskLevel),
    recommendation: mapRecommendation(metric?.recommendation ?? raw.recommendation),
    availability: mapAvailability(raw.is_injured ?? raw.isInjured ?? false, raw.is_suspended ?? raw.isSuspended ?? false),
    marketPrice: raw.current_floor_price ?? raw.currentFloorPrice ?? 0,
    priceChange7d: 0,
    injury,
    suspension,
    scores: mappedScores,
    analysis,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapClub(raw: any): Club {
  return {
    id: sid(raw.id),
    name: raw.name ?? "",
    shortName: raw.short_name ?? raw.shortName ?? raw.name?.slice(0, 3).toUpperCase() ?? "",
    competition: raw.competition?.name ?? raw.competition ?? "",
    country: raw.country ?? "",
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapGameweek(raw: any): Gameweek {
  const stateMap: Record<string, Gameweek["status"]> = {
    opened: "LIVE",
    live: "LIVE",
    upcoming: "UPCOMING",
    closed: "COMPLETED",
  };
  return {
    id: raw.game_week ?? raw.gameWeek ?? raw.id ?? 0,
    label: raw.event_name ?? raw.eventName ?? `GW ${raw.game_week ?? raw.gameWeek ?? ""}`,
    startDate: raw.start_date ?? raw.startDate ?? "",
    endDate: raw.end_date ?? raw.endDate ?? "",
    status: stateMap[raw.state] ?? "UPCOMING",
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapFixture(raw: any): Fixture {
  return {
    id: sid(raw.id),
    gameweek: 0,
    date: raw.date ?? "",
    competition: raw.competition?.name ?? raw.competition ?? "",
    homeClubId: sid(raw.home_club_id ?? raw.homeClubId),
    awayClubId: sid(raw.away_club_id ?? raw.awayClubId),
    homeClub: raw.home_club?.name ?? raw.homeClub?.name ?? raw.homeClub ?? "",
    awayClub: raw.away_club?.name ?? raw.awayClub?.name ?? raw.awayClub ?? "",
    difficulty: 3,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapPlayerFixture(raw: any, playerClubId?: string): PlayerFixture {
  const fixture = mapFixture(raw);
  const isHome = playerClubId ? fixture.homeClubId === playerClubId : true;
  return {
    fixture,
    isHome,
    opponent: isHome ? fixture.awayClub : fixture.homeClub,
    difficulty: fixture.difficulty,
    expectedMinutes: 90,
    projectedScore: 0,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapMarketData(raw: any): MarketData {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const history: PricePoint[] = (raw.price_history ?? raw.priceHistory ?? []).map((p: any) => ({
    date: p.observed_at ?? p.observedAt ?? "",
    price: p.average_price ?? p.averagePrice ?? p.price ?? 0,
  }));

  return {
    playerId: sid(raw.player_id ?? raw.playerId),
    currentPrice: raw.current_floor_price ?? raw.currentFloorPrice ?? 0,
    lowestAsk: raw.current_floor_price ?? raw.currentFloorPrice ?? 0,
    change24h: 0,
    change7d: raw.change_7d_pct ?? raw.change7dPct ?? 0,
    change30d: raw.change_30d_pct ?? raw.change30dPct ?? 0,
    volume7d: raw.volume_30d ?? raw.volume30d ?? 0,
    trend: (raw.change_7d_pct ?? raw.change7dPct ?? 0) > 0 ? "UP" : (raw.change_7d_pct ?? raw.change7dPct ?? 0) < 0 ? "DOWN" : "FLAT",
    history,
    recentSales: [],
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapMarketOverview(raw: any): MarketOverview {
  const topGainers = raw.top_gainers ?? raw.topGainers ?? [];
  const topLosers = raw.top_losers ?? raw.topLosers ?? [];
  const opps = raw.opportunities ?? [];
  const trending = raw.trending ?? [];

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function moverToPlayer(m: any): Player {
    return {
      id: sid(m.player_id ?? m.playerId),
      name: m.player_name ?? m.playerName ?? "",
      age: 0,
      position: mapPosition(m.position ?? "Midfielder"),
      clubId: "",
      club: m.club_name ?? m.clubName ?? "",
      competition: "",
      nationality: "",
      photoUrl: m.image_url ?? m.imageUrl ?? undefined,
      averageScore: 0,
      form: 0,
      projectedScore: 0,
      startingProbability: 50,
      minutesShare: 50,
      consistency: 50,
      ceiling: 65,
      floor: 35,
      scoutScore: m.scout_score ?? m.scoutScore ?? 0,
      risk: "LOW",
      recommendation: "HOLD",
      availability: "AVAILABLE",
      marketPrice: m.current_price ?? m.currentPrice ?? 0,
      priceChange7d: m.change_pct ?? m.changePct ?? 0,
      injury: { status: "AVAILABLE", provenance: "FACT", updatedAt: new Date().toISOString() },
      suspension: { suspended: false, provenance: "FACT" },
      scores: [],
      analysis: { strengths: [], weaknesses: [], opportunity: "", riskFactors: [], scoutScoreExplanation: "", confidence: "MEDIUM" },
    };
  }

  return {
    totalVolume7d: raw.total_volume_24h ?? raw.totalVolume24h ?? 0,
    activeListings: raw.active_listings_count ?? raw.activeListingsCount ?? 0,
    medianPrice: 0,
    indexChange7d: 0,
    risers: topGainers.map(moverToPlayer),
    fallers: topLosers.map(moverToPlayer),
    undervalued: opps.map(moverToPlayer),
    highVolume: trending.map(moverToPlayer),
    recentSales: [],
    indexHistory: [],
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapCard(raw: any): Card {
  return {
    id: sid(raw.id),
    playerId: sid(raw.player_id ?? raw.playerId),
    player: raw.player ? mapPlayer(raw.player) : ({} as Player),
    rarity: mapRarity(raw.rarity),
    season: String(raw.season_year ?? raw.seasonYear ?? ""),
    serial: 1,
    acquiredPrice: raw.latest_price ?? raw.latestPrice ?? 0,
    price: raw.latest_price ?? raw.latestPrice ?? 0,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapWatchlistEntry(raw: any): WatchlistEntry {
  return {
    id: sid(raw.id),
    playerId: sid(raw.player_id ?? raw.playerId),
    player: raw.player ? mapPlayer(raw.player) : ({} as Player),
    addedAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    targetPrice: raw.target_price ?? raw.targetPrice ?? undefined,
    latestAlert: raw.notes ?? undefined,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapAlert(raw: any): Alert {
  return {
    id: sid(raw.id),
    category: mapAlertCategory(raw.type ?? raw.category ?? "Performance"),
    severity: mapSeverity(raw.severity ?? "INFO"),
    title: raw.title ?? "",
    detail: raw.message ?? raw.detail ?? "",
    playerId: raw.player_id != null || raw.playerId != null ? sid(raw.player_id ?? raw.playerId) : undefined,
    playerName: raw.player_name ?? raw.playerName ?? undefined,
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    read: raw.read ?? false,
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapNewsArticle(raw: any): NewsArticle {
  const players = raw.players ?? [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const firstPlayer = players[0] as any;
  return {
    id: sid(raw.id),
    headline: raw.title ?? "",
    summary: raw.summary ?? "",
    source: raw.source ?? "",
    sourceUrl: raw.url ?? undefined,
    publishedAt: raw.published_at ?? raw.publishedAt ?? "",
    playerId: firstPlayer ? sid(firstPlayer.id) : undefined,
    playerName: firstPlayer?.display_name ?? firstPlayer?.displayName ?? undefined,
    club: undefined,
    category: mapNewsCategory(raw.category ?? "Club News"),
    confidence: "MEDIUM",
    provenance: raw.source_type ?? raw.sourceType ?? "REPORT",
  };
}

function mapNewsCategory(raw: string): NewsArticle["category"] {
  const map: Record<string, NewsArticle["category"]> = {
    injury: "Injury",
    transfer: "Transfer",
    tactical: "Starting XI",
    general: "Club News",
    Injury: "Injury",
    Transfer: "Transfer",
    "Starting XI": "Starting XI",
    Suspension: "Suspension",
    Performance: "Performance",
    "Club News": "Club News",
  };
  return map[raw] ?? "Club News";
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapGroupMember(raw: any): GroupMember {
  return {
    id: sid(raw.user_id ?? raw.userId ?? raw.id),
    rank: raw.rank ?? 0,
    previousRank: raw.rank ?? 0,
    username: raw.username ?? "",
    gameweekPoints: raw.weekly_points ?? raw.weeklyPoints ?? 0,
    overallPoints: raw.weekly_points ?? raw.weeklyPoints ?? 0,
    squadValue: raw.squad_value_eur ?? raw.squadValueEur ?? 0,
    cards: raw.total_cards ?? raw.totalCards ?? 0,
  };
}

// ---------------------------------------------------------------------------
// REST API factory
// ---------------------------------------------------------------------------

type HttpFnType = <T>(path: string, init?: RequestInit) => Promise<T>;

export function createRestApi(http: HttpFnType): ScoutlabApi {
  const API = "/api/v1";

  return {
    // -----------------------------------------------------------------------
    // Metadata & Lookups
    // -----------------------------------------------------------------------
    async getDataFreshness(): Promise<DataFreshness> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/dashboard`);
      const dash = unwrap(envelope);
      const gw = dash.current_gameweek ?? dash.currentGameweek;
      const freshness = dash.data_freshness ?? dash.dataFreshness;

      return {
        lastUpdated: freshness?.last_sync_at ?? freshness?.lastSyncAt ?? new Date().toISOString(),
        minutesAgo: 0,
        status: (freshness?.status === "fresh" ? "FRESH" : freshness?.status === "syncing" ? "SYNCING" : "STALE") as DataFreshness["status"],
        gameweek: gw
          ? mapGameweek(gw)
          : { id: 0, label: "N/A", startDate: "", endDate: "", status: "UPCOMING" },
      };
    },

    async getGameweeks(): Promise<Gameweek[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/fixtures/gameweeks`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapGameweek);
    },

    async getClubs(): Promise<Club[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/clubs`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapClub);
    },

    async getCompetitions(): Promise<string[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/competitions`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map((c: any) => c.name ?? "");
    },

    // -----------------------------------------------------------------------
    // Dashboard & Scouting
    // -----------------------------------------------------------------------
    async getDashboardKpis(): Promise<DashboardKpis> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/dashboard`);
      const dash = unwrap(envelope);

      return {
        squadValue: dash.squad_value_eur ?? dash.squadValueEur ?? 0,
        squadValueChange: 0,
        squadAverageScore: dash.average_score_l5 ?? dash.averageScoreL5 ?? 0,
        squadAverageScoreChange: 0,
        playersInForm: (dash.players_in_form ?? dash.playersInForm ?? []).length,
        playersAtRisk: (dash.players_at_risk ?? dash.playersAtRisk ?? []).length,
        marketOpportunities: (dash.market_opportunities ?? dash.marketOpportunities ?? []).length,
        upcomingFixtures: (dash.upcoming_fixtures ?? dash.upcomingFixtures ?? []).length,
      };
    },

    async getScoutingOpportunities(limit = 12): Promise<Player[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(
        `${API}/players?sort_by=scout_score&sort_order=desc&page_size=${limit}`,
      );
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapPlayer);
    },

    // -----------------------------------------------------------------------
    // Players
    // -----------------------------------------------------------------------
    async searchPlayers(query: ScoutQuery): Promise<Paginated<Player>> {
      const params = new URLSearchParams();

      if (query.search) params.set("search", query.search);
      if (query.positions?.length) {
        // Backend accepts one position at a time with full names
        const posMap: Record<string, string> = { GK: "Goalkeeper", DEF: "Defender", MID: "Midfielder", FWD: "Forward" };
        params.set("position", query.positions.map((p) => posMap[p] ?? p).join(","));
      }
      if (query.clubs?.length) params.set("club", query.clubs[0]);
      if (query.competitions?.length) params.set("competition", query.competitions[0]);
      if (query.ageMax != null) params.set("age_max", String(query.ageMax));
      if (query.priceMax != null) params.set("price_max", String(query.priceMax));
      if (query.minAverageScore != null) params.set("score_min", String(query.minAverageScore));
      if (query.minForm != null) params.set("form_min", String(query.minForm));
      if (query.minStartingProbability != null) params.set("starting_probability_min", String(query.minStartingProbability));
      if (query.minScoutScore != null) params.set("score_min", String(query.minScoutScore));
      if (query.excludeInjured) params.set("injury_status", "fit");
      if (query.recommendations?.length) params.set("recommendation", query.recommendations[0]);

      // Sorting
      const sortMap: Record<string, string> = {
        scoutScore: "scout_score",
        form: "form_score",
        age: "age",
        name: "name",
        marketPrice: "price",
        startingProbability: "starting_probability",
      };
      if (query.sortBy) params.set("sort_by", sortMap[query.sortBy as string] ?? "scout_score");
      if (query.sortDir) params.set("sort_order", query.sortDir);

      params.set("page", String(query.page ?? 1));
      params.set("page_size", String(query.pageSize ?? 25));

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/players?${params.toString()}`);
      const items = unwrap(envelope);
      const meta = envelope.meta;

      return {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        items: (items as any[]).map(mapPlayer),
        total: meta?.total ?? 0,
        page: meta?.page ?? 1,
        pageSize: meta?.page_size ?? meta?.pageSize ?? 25,
      };
    },

    async getPlayer(id: string): Promise<Player> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/players/${id}`);
      return mapPlayer(unwrap(envelope));
    },

    async getPlayerMarket(id: string): Promise<MarketData> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/players/${id}/market`);
      return mapMarketData(unwrap(envelope));
    },

    async getPlayerFixtures(id: string): Promise<PlayerFixture[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/players/${id}/fixtures`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map((g: any) => mapPlayerFixture(g));
    },

    // -----------------------------------------------------------------------
    // Market
    // -----------------------------------------------------------------------
    async getMarketOverview(): Promise<MarketOverview> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/market`);
      return mapMarketOverview(unwrap(envelope));
    },

    async getFixtures(filters): Promise<Fixture[]> {
      const params = new URLSearchParams();
      if (filters?.competition) params.set("competition_id", filters.competition);
      if (filters?.clubId) params.set("club_id", filters.clubId);
      params.set("page_size", "100");

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/fixtures?${params.toString()}`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapFixture);
    },

    // -----------------------------------------------------------------------
    // Portfolio & Cards
    // -----------------------------------------------------------------------
    async getMyCards(): Promise<Card[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/cards?page_size=100`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapCard);
    },

    async getPortfolioSummary(): Promise<PortfolioSummary> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/portfolio/summary`);
      const data = unwrap(envelope);
      return {
        totalValue: data.total_value ?? data.totalValue ?? 0,
        change7d: data.change_7d ?? data.change7d ?? 0,
        changePct7d: data.change_pct_7d ?? data.changePct7d ?? 0,
        averageScore: data.average_score ?? data.averageScore ?? 0,
        cardCount: data.card_count ?? data.cardCount ?? 0,
        atRisk: data.at_risk ?? data.atRisk ?? 0,
      };
    },

    // -----------------------------------------------------------------------
    // Watchlist
    // -----------------------------------------------------------------------
    async getWatchlist(): Promise<WatchlistEntry[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/watchlist`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapWatchlistEntry);
    },

    async addToWatchlist(playerId: string): Promise<WatchlistEntry[]> {
      await http(`${API}/watchlist/${playerId}`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      // Re-fetch the full list (backend returns single item)
      return this.getWatchlist();
    },

    async removeFromWatchlist(playerId: string): Promise<WatchlistEntry[]> {
      await http(`${API}/watchlist/${playerId}`, { method: "DELETE" });
      return this.getWatchlist();
    },

    // -----------------------------------------------------------------------
    // News
    // -----------------------------------------------------------------------
    async getNews(filters): Promise<NewsArticle[]> {
      const params = new URLSearchParams();
      if (filters?.category) {
        const catMap: Record<string, string> = {
          Injury: "injury",
          Transfer: "transfer",
          "Starting XI": "tactical",
          Suspension: "general",
          Performance: "general",
          "Club News": "general",
        };
        params.set("category", catMap[filters.category] ?? "general");
      }
      params.set("page_size", "50");

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/news?${params.toString()}`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapNewsArticle);
    },

    // -----------------------------------------------------------------------
    // Group
    // -----------------------------------------------------------------------
    async getGroupMembers(): Promise<GroupMember[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/group/ranking`);
      const data = unwrap(envelope);
      const rankings = data.rankings ?? [];
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (rankings as any[]).map(mapGroupMember);
    },

    // -----------------------------------------------------------------------
    // Alerts
    // -----------------------------------------------------------------------
    async getAlerts(): Promise<Alert[]> {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const envelope = await http<any>(`${API}/alerts`);
      const items = unwrap(envelope);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (items as any[]).map(mapAlert);
    },

    async markAlertRead(id: string): Promise<Alert[]> {
      await http(`${API}/alerts/${id}/read`, { method: "POST" });
      return this.getAlerts();
    },

    async markAllAlertsRead(): Promise<Alert[]> {
      await http(`${API}/alerts/read-all`, { method: "POST" });
      return this.getAlerts();
    },
  };
}
