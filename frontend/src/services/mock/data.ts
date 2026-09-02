import type {
  Alert,
  AlertCategory,
  AvailabilityStatus,
  Card,
  Club,
  Confidence,
  DashboardKpis,
  DataFreshness,
  Fixture,
  Gameweek,
  GroupMember,
  MarketData,
  MarketOverview,
  NewsArticle,
  NewsCategory,
  Player,
  PlayerScore,
  Position,
  PricePoint,
  Rarity,
  Recommendation,
  RiskLevel,
  WatchlistEntry,
} from "@/types";

/* ------------------------------------------------------------------ *
 * Deterministic pseudo-random generator (stable between SSR & client)
 * ------------------------------------------------------------------ */
function makeRng(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}
const rng = makeRng(20260902);
const rand = (min: number, max: number) => min + rng() * (max - min);
const randInt = (min: number, max: number) => Math.floor(rand(min, max + 1));
const pick = <T,>(arr: readonly T[]): T => arr[randInt(0, arr.length - 1)]!;
const round = (n: number, d = 1) => Number(n.toFixed(d));

/* Anchor "now" to a fixed instant so mock timestamps are deterministic. */
export const NOW = new Date("2026-09-02T19:00:00.000Z");
const iso = (daysAgo: number) =>
  new Date(NOW.getTime() - daysAgo * 86400000).toISOString();
const isoHours = (hoursAgo: number) =>
  new Date(NOW.getTime() - hoursAgo * 3600000).toISOString();
const isoAhead = (days: number) =>
  new Date(NOW.getTime() + days * 86400000).toISOString();

/* ------------------------------------------------------------------ *
 * Clubs
 * ------------------------------------------------------------------ */
const clubSeed: [string, string, string, string][] = [
  ["Arsenal", "ARS", "Premier League", "England"],
  ["Manchester City", "MCI", "Premier League", "England"],
  ["Liverpool", "LIV", "Premier League", "England"],
  ["Chelsea", "CHE", "Premier League", "England"],
  ["Newcastle United", "NEW", "Premier League", "England"],
  ["Real Madrid", "RMA", "LaLiga", "Spain"],
  ["FC Barcelona", "BAR", "LaLiga", "Spain"],
  ["Atlético Madrid", "ATM", "LaLiga", "Spain"],
  ["Real Sociedad", "RSO", "LaLiga", "Spain"],
  ["Inter", "INT", "Serie A", "Italy"],
  ["AC Milan", "MIL", "Serie A", "Italy"],
  ["Napoli", "NAP", "Serie A", "Italy"],
  ["Atalanta", "ATA", "Serie A", "Italy"],
  ["Bayern München", "BAY", "Bundesliga", "Germany"],
  ["Bayer Leverkusen", "B04", "Bundesliga", "Germany"],
  ["Borussia Dortmund", "BVB", "Bundesliga", "Germany"],
  ["RB Leipzig", "RBL", "Bundesliga", "Germany"],
  ["Paris Saint-Germain", "PSG", "Ligue 1", "France"],
  ["Olympique Marseille", "OM", "Ligue 1", "France"],
  ["Lille", "LIL", "Ligue 1", "France"],
  ["Ajax", "AJA", "Eredivisie", "Netherlands"],
  ["PSV", "PSV", "Eredivisie", "Netherlands"],
  ["Benfica", "SLB", "Liga Portugal", "Portugal"],
  ["Sporting CP", "SCP", "Liga Portugal", "Portugal"],
];

export const clubs: Club[] = clubSeed.map(([name, shortName, competition, country], i) => ({
  id: `club-${i + 1}`,
  name,
  shortName,
  competition,
  country,
}));

export const competitions = Array.from(new Set(clubs.map((c) => c.competition)));

/* ------------------------------------------------------------------ *
 * Players
 * ------------------------------------------------------------------ */
const firstNames = [
  "Lucas","Mateo","Enzo","Rafael","Kai","Noah","Iker","Youssef","Diogo","Emre",
  "Alessandro","Jonas","Milan","Viktor","Andrés","Tobias","Kenan","Malik","Théo","Bruno",
  "Federico","Sebastián","Nico","Arda","Jamal","Rasmus","Dominik","Elias","Ismaël","Gabriel",
  "Adrien","Marco","Joško","Ruben","Xavi","Yannick","Nathan","Ondrej","Simone","Léo",
];
const lastNames = [
  "Ferreira","Bianchi","Nkunku","Baldé","Hoffmann","Van Dijk","Moretti","Kovač","Diallo","Sørensen",
  "Almeida","Öztürk","Rossi","Lindgren","Rodríguez","Meunier","Novák","Bergström","Fofana","Silva",
  "Konaté","Weber","Marchetti","Petrov","Jansen","Barros","Dumont","Halilović","Okafor","Larsen",
  "Castillo","Meyer","Ortega","Vranjić","Kamara","Ricci","Boateng","Persson","Duarte","Yilmaz",
];
const nationalities = [
  "France","Brazil","Spain","Germany","Italy","Portugal","Netherlands","Argentina","England",
  "Croatia","Senegal","Denmark","Turkey","Morocco","Belgium","Sweden","Czechia","Nigeria","Uruguay","Japan",
];

const positions: Position[] = ["GK", "DEF", "MID", "FWD"];

function availabilityFor(i: number): AvailabilityStatus {
  const m = i % 17;
  if (m === 3) return "INJURED";
  if (m === 9) return "DOUBTFUL";
  if (m === 14) return "SUSPENDED";
  return "AVAILABLE";
}

function recommendationFor(scoutScore: number, risk: RiskLevel, avail: AvailabilityStatus): Recommendation {
  if (avail === "INJURED" || avail === "SUSPENDED") return "AVOID";
  if (scoutScore >= 80 && risk !== "HIGH") return "BUY";
  if (scoutScore >= 70) return "WATCH";
  if (scoutScore >= 55) return "HOLD";
  if (scoutScore >= 42) return "SELL";
  return "AVOID";
}

function buildScores(base: number, seedIdx: number): PlayerScore[] {
  const out: PlayerScore[] = [];
  for (let gw = 1; gw <= 12; gw++) {
    const minutes = rng() > 0.16 ? randInt(62, 90) : randInt(8, 55);
    const noise = rand(-16, 18);
    const score = Math.max(4, Math.min(98, base + noise * (minutes < 60 ? 1.4 : 1)));
    out.push({
      gameweek: gw,
      date: iso((13 - gw) * 7),
      opponent: clubs[(seedIdx + gw) % clubs.length]!.shortName,
      score: round(score),
      projected: round(Math.max(6, base + rand(-6, 6))),
      minutes,
      decisiveScore: round(score * rand(0.2, 0.45)),
      allAroundScore: round(score * rand(0.55, 0.8)),
    });
  }
  return out;
}

function buildPriceHistory(current: number): PricePoint[] {
  const out: PricePoint[] = [];
  let p = current * rand(0.72, 1.28);
  for (let d = 89; d >= 0; d--) {
    p = Math.max(current * 0.45, p * rand(0.985, 1.016));
    out.push({ date: iso(d), price: round(p, 3) });
  }
  out[out.length - 1] = { date: iso(0), price: current };
  return out;
}

const strengthPool = [
  "Elite decisive output in the final third",
  "Consistently completes 90 minutes",
  "Set-piece taker — inflates all-around score",
  "High progressive passing volume",
  "Dominant in aerial duels",
  "Penalty taker for his club",
  "Strong underlying xG per 90",
  "Excellent recovery numbers from deep",
];
const weaknessPool = [
  "Score variance is high week to week",
  "Rotated in continental competitions",
  "Low involvement in defensive phases",
  "Discipline risk — 4 yellows this season",
  "Struggles against low blocks",
  "Minutes managed after recent return",
  "Limited attacking returns for the position",
];
const riskPool = [
  "Manager has publicly hinted at rotation",
  "Fixture congestion over the next 3 gameweeks",
  "Transfer speculation could affect minutes",
  "Recent injury history in the same muscle group",
  "Price already reflects a strong run of form",
  "Club faces two top-4 opponents next",
];

export const players: Player[] = Array.from({ length: 180 }, (_, i) => {
  const club = clubs[i % clubs.length]!;
  const position = positions[randInt(0, 3)]!;
  const age = randInt(17, 35);
  const base = rand(24, 78);
  const averageScore = round(base);
  const form = round(Math.max(5, Math.min(99, base + rand(-14, 16))));
  const projectedScore = round(Math.max(6, base + rand(-8, 10)));
  const startingProbability = Math.round(rand(28, 99));
  const minutesShare = Math.round(rand(30, 98));
  const consistency = Math.round(rand(35, 95));
  const ceiling = round(Math.min(110, base + rand(14, 34)));
  const floor = round(Math.max(2, base - rand(12, 30)));
  const risk: RiskLevel = consistency > 74 ? "LOW" : consistency > 55 ? "MEDIUM" : "HIGH";
  const availability = availabilityFor(i);
  const scoutScore = Math.round(
    Math.max(
      12,
      Math.min(
        99,
        averageScore * 0.42 +
          form * 0.2 +
          startingProbability * 0.18 +
          consistency * 0.14 +
          rand(-6, 10) +
          (availability === "AVAILABLE" ? 6 : -12),
      ),
    ),
  );
  const marketPrice = round(
    Math.max(0.4, (scoutScore / 100) ** 2.6 * rand(24, 70) + rand(0.3, 3)),
    2,
  );
  const priceChange7d = round(rand(-22, 26), 1);
  const name = `${firstNames[i % firstNames.length]} ${lastNames[(i * 7) % lastNames.length]}`;

  return {
    id: `player-${i + 1}`,
    name,
    age,
    position,
    clubId: club.id,
    club: club.name,
    competition: club.competition,
    nationality: nationalities[i % nationalities.length]!,
    averageScore,
    form,
    projectedScore,
    startingProbability,
    minutesShare,
    consistency,
    ceiling,
    floor,
    scoutScore,
    risk,
    recommendation: recommendationFor(scoutScore, risk, availability),
    availability,
    marketPrice,
    priceChange7d,
    injury: {
      status: availability,
      description:
        availability === "INJURED"
          ? pick(["Hamstring strain", "Ankle sprain", "Knee — meniscus", "Adductor issue"])
          : availability === "DOUBTFUL"
            ? "Knock picked up in training — assessed on matchday"
            : undefined,
      expectedReturn:
        availability === "INJURED" ? isoAhead(randInt(6, 45)) : undefined,
      provenance: availability === "DOUBTFUL" ? "REPORT" : "FACT",
      source: availability === "DOUBTFUL" ? "Club press conference" : "Official club statement",
      updatedAt: isoHours(randInt(2, 70)),
    },
    suspension: {
      suspended: availability === "SUSPENDED",
      reason: availability === "SUSPENDED" ? "Red card — serious foul play" : undefined,
      matchesRemaining: availability === "SUSPENDED" ? randInt(1, 3) : 0,
      provenance: "FACT",
    },
    scores: buildScores(base, i),
    analysis: {
      strengths: [strengthPool[i % strengthPool.length]!, strengthPool[(i * 3 + 2) % strengthPool.length]!],
      weaknesses: [weaknessPool[i % weaknessPool.length]!, weaknessPool[(i * 5 + 1) % weaknessPool.length]!],
      opportunity:
        priceChange7d < -6
          ? "Price has corrected faster than underlying output — mispricing window."
          : "Fixture run over the next three gameweeks favours attacking returns.",
      riskFactors: [riskPool[i % riskPool.length]!, riskPool[(i * 2 + 3) % riskPool.length]!],
      scoutScoreExplanation:
        "Scout Score blends average score (42%), recent form (20%), starting XI probability (18%) and consistency (14%), adjusted for availability and fixture difficulty.",
      confidence: (consistency > 72 ? "HIGH" : consistency > 52 ? "MEDIUM" : "LOW") as Confidence,
    },
  };
});

export const playersById = new Map(players.map((p) => [p.id, p]));

/* ------------------------------------------------------------------ *
 * Market
 * ------------------------------------------------------------------ */
export const marketByPlayer = new Map<string, MarketData>(
  players.map((p) => {
    const history = buildPriceHistory(p.marketPrice);
    return [
      p.id,
      {
        playerId: p.id,
        currentPrice: p.marketPrice,
        lowestAsk: round(p.marketPrice * rand(0.9, 0.99), 2),
        change24h: round(rand(-8, 9), 1),
        change7d: p.priceChange7d,
        change30d: round(rand(-30, 38), 1),
        volume7d: randInt(3, 180),
        trend: p.priceChange7d > 2 ? "UP" : p.priceChange7d < -2 ? "DOWN" : "FLAT",
        history,
        recentSales: Array.from({ length: 6 }, (_, k) => ({
          date: iso(k * rand(0.4, 2)),
          price: round(p.marketPrice * rand(0.88, 1.12), 2),
          rarity: pick<Rarity>(["limited", "rare", "super rare"]),
        })),
      } satisfies MarketData,
    ];
  }),
);

/* ------------------------------------------------------------------ *
 * Gameweeks & fixtures
 * ------------------------------------------------------------------ */
export const gameweeks: Gameweek[] = Array.from({ length: 6 }, (_, i) => {
  const gw = 13 + i;
  return {
    id: gw,
    label: `GW ${gw}`,
    startDate: isoAhead(i * 7 - 1),
    endDate: isoAhead(i * 7 + 2),
    status: i === 0 ? "LIVE" : "UPCOMING",
  };
});

export const currentGameweek = gameweeks[0]!;

export const fixtures: Fixture[] = (() => {
  const out: Fixture[] = [];
  gameweeks.forEach((gw, gi) => {
    for (let i = 0; i < clubs.length; i += 2) {
      const home = clubs[(i + gi) % clubs.length]!;
      const away = clubs[(i + gi + 1) % clubs.length]!;
      if (home.id === away.id) continue;
      out.push({
        id: `fx-${gw.id}-${i}`,
        gameweek: gw.id,
        date: isoAhead(gi * 7 + (i % 3)),
        competition: home.competition,
        homeClubId: home.id,
        awayClubId: away.id,
        homeClub: home.name,
        awayClub: away.name,
        difficulty: randInt(1, 5),
      });
    }
  });
  return out;
})();

/* ------------------------------------------------------------------ *
 * Portfolio (My Cards)
 * ------------------------------------------------------------------ */
const rarities: Rarity[] = ["limited", "rare", "super rare"];
export const cards: Card[] = Array.from({ length: 14 }, (_, i) => {
  const player = players[(i * 11 + 4) % players.length]!;
  return {
    id: `card-${i + 1}`,
    playerId: player.id,
    player,
    rarity: rarities[i % rarities.length]!,
    season: pick(["2024-25", "2025-26", "In Season"]),
    serial: randInt(1, 100),
    acquiredPrice: round(player.marketPrice * rand(0.6, 1.3), 2),
    price: player.marketPrice,
  };
});

/* ------------------------------------------------------------------ *
 * Watchlist
 * ------------------------------------------------------------------ */
export const watchlist: WatchlistEntry[] = Array.from({ length: 8 }, (_, i) => {
  const player = players[(i * 17 + 5) % players.length]!;
  return {
    id: `wl-${i + 1}`,
    playerId: player.id,
    player,
    addedAt: iso(randInt(1, 40)),
    targetPrice: round(player.marketPrice * 0.85, 2),
    latestAlert:
      i % 3 === 0
        ? `Starting XI probability moved to ${player.startingProbability}%`
        : i % 3 === 1
          ? `Price ${player.priceChange7d > 0 ? "up" : "down"} ${Math.abs(player.priceChange7d)}% over 7 days`
          : "Named in projected lineup by two sources",
  };
});

/* ------------------------------------------------------------------ *
 * News
 * ------------------------------------------------------------------ */
const newsCategories: NewsCategory[] = [
  "Transfer","Injury","Starting XI","Suspension","Performance","Club News",
];
const sources = ["The Athletic","Sky Sports","L'Équipe","Fabrizio Romano","Club Official","Marca","Kicker","BBC Sport"];

export const news: NewsArticle[] = Array.from({ length: 24 }, (_, i) => {
  const player = players[(i * 13 + 2) % players.length]!;
  const category = newsCategories[i % newsCategories.length]!;
  const headlineByCategory: Record<NewsCategory, string> = {
    Transfer: `${player.name} attracting interest ahead of the window`,
    Injury: `${player.name} withdrawn from training with a knock`,
    "Starting XI": `${player.name} expected to start against ${clubs[(i + 3) % clubs.length]!.shortName}`,
    Suspension: `${player.name} one booking from a suspension`,
    Performance: `${player.name} posts season-best display for ${player.club}`,
    "Club News": `${player.club} confirm squad rotation plan for the run of fixtures`,
  };
  return {
    id: `news-${i + 1}`,
    headline: headlineByCategory[category],
    summary:
      category === "Starting XI"
        ? "Two independent outlets list him in the projected line-up. Treat as a report until the team sheet is confirmed."
        : "Details are still developing; ScoutLab will update the record when the club confirms.",
    source: sources[i % sources.length]!,
    publishedAt: isoHours(i * rand(1.2, 5)),
    playerId: player.id,
    playerName: player.name,
    club: player.club,
    category,
    confidence: (i % 3 === 0 ? "HIGH" : i % 3 === 1 ? "MEDIUM" : "LOW") as Confidence,
    provenance: category === "Starting XI" || category === "Transfer" ? "REPORT" : "FACT",
  };
});

/* ------------------------------------------------------------------ *
 * Alerts
 * ------------------------------------------------------------------ */
const alertCategories: AlertCategory[] = [
  "Injury","Suspension","Price","Starting XI","Fixture","Performance",
];

export const alerts: Alert[] = Array.from({ length: 18 }, (_, i) => {
  const player = players[(i * 23 + 7) % players.length]!;
  const category = alertCategories[i % alertCategories.length]!;
  const map: Record<AlertCategory, { title: string; detail: string; severity: Alert["severity"] }> = {
    Injury: {
      title: `${player.name} — injury update`,
      detail: `Club reports a muscular issue. Expected return window: ${randInt(2, 6)} weeks.`,
      severity: "negative",
    },
    Suspension: {
      title: `${player.name} suspended`,
      detail: "Red card in the last fixture. Unavailable for the next match.",
      severity: "negative",
    },
    Price: {
      title: `${player.name} price ${player.priceChange7d > 0 ? "increased" : "dropped"} ${Math.abs(player.priceChange7d)}%`,
      detail: `Floor now ${player.marketPrice.toFixed(2)} ETH on limited.`,
      severity: player.priceChange7d > 0 ? "positive" : "warning",
    },
    "Starting XI": {
      title: `${player.name} starting probability → ${player.startingProbability}%`,
      detail: "Projection updated after the pre-match press conference.",
      severity: "info",
    },
    Fixture: {
      title: `Fixture difficulty changed for ${player.club}`,
      detail: "Opponent rating revised following a squad-availability update.",
      severity: "warning",
    },
    Performance: {
      title: `${player.name} scored ${player.form} last gameweek`,
      detail: "Above projection — form component of Scout Score revised upward.",
      severity: "positive",
    },
  };
  return {
    id: `alert-${i + 1}`,
    category,
    ...map[category],
    playerId: player.id,
    playerName: player.name,
    createdAt: isoHours(i * rand(0.8, 4)),
    read: i > 5,
  };
});

/* ------------------------------------------------------------------ *
 * Group
 * ------------------------------------------------------------------ */
const usernames = [
  "simon","marta","kepler","ivo","nuno","lea","tomas","rui","anouk","dmitri",
];
export const groupMembers: GroupMember[] = usernames
  .map((username, i) => ({
    id: `member-${i + 1}`,
    rank: 0,
    previousRank: randInt(1, 10),
    username,
    gameweekPoints: round(rand(180, 320)),
    overallPoints: round(rand(1900, 3400)),
    squadValue: round(rand(12, 68), 1),
    cards: randInt(8, 26),
  }))
  .sort((a, b) => b.overallPoints - a.overallPoints)
  .map((m, i) => ({ ...m, rank: i + 1 }));

/* ------------------------------------------------------------------ *
 * Aggregates
 * ------------------------------------------------------------------ */
/** Always relative to the real clock so the freshness indicator stays honest. */
export function computeFreshness(): DataFreshness {
  const minutesAgo = 8;
  return {
    lastUpdated: new Date(Date.now() - minutesAgo * 60000).toISOString(),
    minutesAgo,
    status: "FRESH",
    gameweek: currentGameweek,
  };
}

export function computeKpis(): DashboardKpis {
  const squadValue = cards.reduce((s, c) => s + c.price, 0);
  const avg = cards.reduce((s, c) => s + c.player.averageScore, 0) / cards.length;
  return {
    squadValue: round(squadValue, 2),
    squadValueChange: 4.8,
    squadAverageScore: round(avg),
    squadAverageScoreChange: 2.3,
    playersInForm: cards.filter((c) => c.player.form > c.player.averageScore + 4).length,
    playersAtRisk: cards.filter(
      (c) => c.player.availability !== "AVAILABLE" || c.player.risk === "HIGH",
    ).length,
    marketOpportunities: players.filter((p) => p.recommendation === "BUY").length,
    upcomingFixtures: fixtures.filter((f) => f.gameweek === currentGameweek.id).length,
  };
}

export function computeMarketOverview(): MarketOverview {
  const byChange = [...players].sort((a, b) => b.priceChange7d - a.priceChange7d);
  const undervalued = [...players]
    .filter((p) => p.availability === "AVAILABLE")
    .sort((a, b) => b.scoutScore / b.marketPrice - a.scoutScore / a.marketPrice)
    .slice(0, 8);
  const highVolume = [...players]
    .sort(
      (a, b) => (marketByPlayer.get(b.id)?.volume7d ?? 0) - (marketByPlayer.get(a.id)?.volume7d ?? 0),
    )
    .slice(0, 8);
  let idx = 100;
  const indexHistory: PricePoint[] = Array.from({ length: 60 }, (_, k) => {
    idx = idx * rand(0.992, 1.011);
    return { date: iso(59 - k), price: round(idx, 2) };
  });
  return {
    totalVolume7d: round(players.reduce((s, p) => s + (marketByPlayer.get(p.id)?.volume7d ?? 0) * p.marketPrice, 0)),
    activeListings: 4821,
    medianPrice: round(
      [...players].sort((a, b) => a.marketPrice - b.marketPrice)[Math.floor(players.length / 2)]!
        .marketPrice,
      2,
    ),
    indexChange7d: 3.4,
    indexHistory,
    risers: byChange.slice(0, 8),
    fallers: byChange.slice(-8).reverse(),
    undervalued,
    highVolume,
    recentSales: Array.from({ length: 10 }, (_, i) => {
      const p = players[(i * 29 + 3) % players.length]!;
      return {
        id: `sale-${i + 1}`,
        playerName: p.name,
        rarity: rarities[i % rarities.length]!,
        price: round(p.marketPrice * rand(0.9, 1.1), 2),
        date: isoHours(i * rand(0.5, 3)),
      };
    }),
  };
}

export function playerFixtures(player: Player) {
  return fixtures
    .filter((f) => f.homeClubId === player.clubId || f.awayClubId === player.clubId)
    .slice(0, 5)
    .map((f) => {
      const isHome = f.homeClubId === player.clubId;
      return {
        fixture: f,
        isHome,
        opponent: isHome ? f.awayClub : f.homeClub,
        difficulty: f.difficulty,
        expectedMinutes: Math.round((player.minutesShare / 100) * 90),
        projectedScore: round(
          Math.max(5, player.projectedScore - (f.difficulty - 3) * 3 + (isHome ? 2 : -2)),
        ),
      };
    });
}
