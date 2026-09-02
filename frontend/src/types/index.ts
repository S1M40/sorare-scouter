export type Position = "GK" | "DEF" | "MID" | "FWD";
export type Recommendation = "BUY" | "WATCH" | "HOLD" | "SELL" | "AVOID";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type AvailabilityStatus =
  | "AVAILABLE"
  | "DOUBTFUL"
  | "INJURED"
  | "SUSPENDED"
  | "UNAVAILABLE";
export type Rarity = "common" | "limited" | "rare" | "super rare" | "unique";
export type Confidence = "LOW" | "MEDIUM" | "HIGH";
/** Provenance of a data point — never render a PREDICTION as confirmed fact. */
export type Provenance = "FACT" | "REPORT" | "PREDICTION";

export interface Club {
  id: string;
  name: string;
  shortName: string;
  competition: string;
  country: string;
}

export interface InjuryInfo {
  status: AvailabilityStatus;
  description?: string | undefined;
  expectedReturn?: string | undefined;
  provenance: Provenance;
  source?: string | undefined;
  updatedAt: string;
}

export interface SuspensionInfo {
  suspended: boolean;
  reason?: string | undefined;
  matchesRemaining?: number | undefined;
  provenance: Provenance;
}

export interface PlayerScore {
  gameweek: number;
  date: string;
  opponent: string;
  score: number;
  projected: number;
  minutes: number;
  decisiveScore: number;
  allAroundScore: number;
}

export interface PricePoint {
  date: string;
  price: number;
}

export interface MarketData {
  playerId: string;
  currentPrice: number;
  lowestAsk: number;
  change24h: number;
  change7d: number;
  change30d: number;
  volume7d: number;
  trend: "UP" | "DOWN" | "FLAT";
  history: PricePoint[];
  recentSales: { date: string; price: number; rarity: Rarity }[];
}

export interface Fixture {
  id: string;
  gameweek: number;
  date: string;
  competition: string;
  homeClubId: string;
  awayClubId: string;
  homeClub: string;
  awayClub: string;
  difficulty: number;
}

export interface PlayerFixture {
  fixture: Fixture;
  isHome: boolean;
  opponent: string;
  difficulty: number;
  expectedMinutes: number;
  projectedScore: number;
}

export interface ScoutingAnalysis {
  strengths: string[];
  weaknesses: string[];
  opportunity: string;
  riskFactors: string[];
  scoutScoreExplanation: string;
  confidence: Confidence;
}

export interface Player {
  id: string;
  name: string;
  age: number;
  position: Position;
  clubId: string;
  club: string;
  competition: string;
  nationality: string;
  photoUrl?: string | undefined;
  averageScore: number;
  form: number;
  projectedScore: number;
  startingProbability: number;
  minutesShare: number;
  consistency: number;
  ceiling: number;
  floor: number;
  scoutScore: number;
  risk: RiskLevel;
  recommendation: Recommendation;
  availability: AvailabilityStatus;
  marketPrice: number;
  priceChange7d: number;
  injury: InjuryInfo;
  suspension: SuspensionInfo;
  scores: PlayerScore[];
  analysis: ScoutingAnalysis;
}

export interface Card {
  id: string;
  playerId: string;
  player: Player;
  rarity: Rarity;
  season: string;
  serial: number;
  acquiredPrice: number;
  price: number;
}

export interface Gameweek {
  id: number;
  label: string;
  startDate: string;
  endDate: string;
  status: "LIVE" | "UPCOMING" | "COMPLETED";
}

export type NewsCategory =
  | "Transfer"
  | "Injury"
  | "Starting XI"
  | "Suspension"
  | "Performance"
  | "Club News";

export interface NewsArticle {
  id: string;
  headline: string;
  summary: string;
  source: string;
  sourceUrl?: string | undefined;
  publishedAt: string;
  playerId?: string | undefined;
  playerName?: string | undefined;
  club?: string | undefined;
  category: NewsCategory;
  confidence: Confidence;
  provenance: Provenance;
}

export type AlertCategory =
  | "Injury"
  | "Suspension"
  | "Price"
  | "Starting XI"
  | "Fixture"
  | "Performance";

export interface Alert {
  id: string;
  category: AlertCategory;
  severity: "info" | "positive" | "warning" | "negative";
  title: string;
  detail: string;
  playerId?: string | undefined;
  playerName?: string | undefined;
  createdAt: string;
  read: boolean;
}

export interface WatchlistEntry {
  id: string;
  playerId: string;
  player: Player;
  addedAt: string;
  targetPrice?: number | undefined;
  latestAlert?: string | undefined;
}

export interface GroupMember {
  id: string;
  rank: number;
  previousRank: number;
  username: string;
  gameweekPoints: number;
  overallPoints: number;
  squadValue: number;
  cards: number;
}

export interface DashboardKpis {
  squadValue: number;
  squadValueChange: number;
  squadAverageScore: number;
  squadAverageScoreChange: number;
  playersInForm: number;
  playersAtRisk: number;
  marketOpportunities: number;
  upcomingFixtures: number;
}

export interface MarketOverview {
  totalVolume7d: number;
  activeListings: number;
  medianPrice: number;
  indexChange7d: number;
  risers: Player[];
  fallers: Player[];
  undervalued: Player[];
  highVolume: Player[];
  recentSales: {
    id: string;
    playerName: string;
    rarity: Rarity;
    price: number;
    date: string;
  }[];
  indexHistory: PricePoint[];
}

export interface DataFreshness {
  lastUpdated: string;
  minutesAgo: number;
  status: "FRESH" | "STALE" | "SYNCING";
  gameweek: Gameweek;
}

export interface ScoutFilters {
  search?: string;
  positions?: Position[];
  clubs?: string[];
  competitions?: string[];
  ageMax?: number;
  priceMax?: number;
  minAverageScore?: number;
  minForm?: number;
  minProjected?: number;
  minStartingProbability?: number;
  minMinutesShare?: number;
  excludeInjured?: boolean;
  excludeSuspended?: boolean;
  minScoutScore?: number;
  risk?: RiskLevel[];
  recommendations?: Recommendation[];
}

export interface SavedFilter {
  id: string;
  name: string;
  filters: ScoutFilters;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface PortfolioSummary {
  totalValue: number;
  change7d: number;
  changePct7d: number;
  averageScore: number;
  cardCount: number;
  atRisk: number;
}
