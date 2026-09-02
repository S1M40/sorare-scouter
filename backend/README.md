# ScoutLab Backend — Production FastAPI Service

ScoutLab is a private football intelligence and scouting platform built for Sorare collectors and syndicates. It replaces mock frontends (e.g. Lovable) with a production-grade, modular, testable, and explainable backend.

---

## 1. Architecture Overview

```
Lovable / Web Frontend
         │  (HTTPS / REST / CORS)
         ▼
FastAPI Application (Port 8000)
 ├── Middleware: CORS, Request Timing, Structured JSON Logging, Global Exception Handling
 ├── API Endpoints (/api/v1):
 │    ├── /dashboard     - Gameweek overview, squad valuation, in-form/at-risk players, market opps
 │    ├── /players       - Multi-field filtering, scout scores, full profile, fixtures, scores, market
 │    ├── /cards         - Card inventory, rarity, grade, pricing observations
 │    ├── /fixtures      - SO5 gameweeks, match schedule & results
 │    ├── /market        - Gainers, losers, trending cards, undervaluation opportunities
 │    ├── /watchlist     - Private user target price alerts and monitoring
 │    ├── /alerts        - Actionable notifications (injuries, price drops, lineups)
 │    ├── /news          - Tactical, injury, and transfer reports linked to players
 │    ├── /group         - Private syndicate rankings, leaderboard, and valuations
 │    └── /auth          - Registration, login, and JWT access tokens
 ├── Services Layer      - Business logic, analytics orchestration, caching coordination
 ├── Repositories Layer  - Async SQLAlchemy 2.0 queries, eager joins, and transactions
 ├── Database            - PostgreSQL (Production / Docker) & Async SQLite (Offline / Test Fallback)
 ├── Redis               - Caching (TTL keys), distributed synchronization locks, rate limiting
 ├── Analytics Engine    - Deterministic, explainable scoring (Form, Consistency, Minutes, Fixture, Availability, Market, Scout Score 0-100, Starting XI Prediction, Multi-signal Risk Engine)
 └── Background Workers  - 30-minute periodic data sync jobs & Sorare ActionCable WebSocket listener
```

---

## 2. Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app creation, lifespan, middleware
│   ├── config.py                # Pydantic Settings & environment variables
│   ├── database.py              # Async SQLAlchemy engine, session maker, get_db dependency
│   │
│   ├── api/
│   │   ├── router.py            # Central v1 router aggregation
│   │   ├── deps.py              # Authentication dependencies (get_current_user)
│   │   └── endpoints/
│   │       ├── dashboard.py     # GET /api/v1/dashboard
│   │       ├── players.py       # GET /api/v1/players and player sub-endpoints
│   │       ├── cards.py         # GET /api/v1/cards, /cards/{id}/prices
│   │       ├── fixtures.py      # GET /api/v1/fixtures, /fixtures/gameweeks
│   │       ├── market.py        # GET /api/v1/market, /market/movers, /opportunities
│   │       ├── watchlist.py     # GET, POST, DELETE /api/v1/watchlist
│   │       ├── alerts.py        # GET, POST /api/v1/alerts
│   │       ├── news.py          # GET /api/v1/news
│   │       ├── group.py         # GET /api/v1/group, /group/ranking
│   │       ├── auth.py          # POST /auth/register, /auth/login, GET /auth/me
│   │       └── health.py        # GET /health
│   │
│   ├── models/                  # SQLAlchemy 2.x declarative models
│   │   ├── base.py
│   │   ├── club.py
│   │   ├── competition.py
│   │   ├── player.py
│   │   ├── game.py
│   │   ├── score.py
│   │   ├── injury.py
│   │   ├── suspension.py
│   │   ├── card.py
│   │   ├── fixture.py
│   │   ├── metric.py
│   │   ├── news.py
│   │   ├── watchlist.py
│   │   ├── alert.py
│   │   ├── user.py
│   │   └── sync_status.py
│   │
│   ├── schemas/                 # Pydantic v2 schemas and response envelopes
│   │   ├── common.py            # ApiResponse[T], ApiListResponse[T], Enums
│   │   ├── dashboard.py
│   │   ├── player.py
│   │   ├── card.py
│   │   ├── fixture.py
│   │   ├── market.py
│   │   ├── metric.py
│   │   ├── news.py
│   │   ├── watchlist.py
│   │   ├── alert.py
│   │   ├── group.py
│   │   ├── auth.py
│   │   └── health.py
│   │
│   ├── repositories/            # Data access layer
│   │   ├── base.py
│   │   ├── player_repository.py
│   │   ├── card_repository.py
│   │   ├── fixture_repository.py
│   │   ├── market_repository.py
│   │   ├── watchlist_repository.py
│   │   ├── alert_repository.py
│   │   ├── news_repository.py
│   │   ├── user_repository.py
│   │   └── sync_repository.py
│   │
│   ├── services/                # Business logic layer
│   │   ├── player_service.py
│   │   ├── card_service.py
│   │   ├── fixture_service.py
│   │   ├── market_service.py
│   │   ├── watchlist_service.py
│   │   ├── alert_service.py
│   │   ├── news_service.py
│   │   ├── group_service.py
│   │   ├── dashboard_service.py
│   │   ├── auth_service.py
│   │   └── sync_service.py
│   │
│   ├── analytics/               # Explainable intelligence engines
│   │   ├── form.py              # Exponential moving average of recent scores
│   │   ├── consistency.py       # Variance and score standard deviation
│   │   ├── minutes.py           # Playing time percentage
│   │   ├── fixture.py           # Match difficulty index & home advantage
│   │   ├── availability.py      # Medical / disciplinary availability
│   │   ├── market.py            # Valuation vs 30-day baseline
│   │   ├── scout_score.py       # Configurable weighted composite score (0-100)
│   │   ├── starting_probability.py # Deterministic prediction (labeled PREDICTION)
│   │   ├── risk_engine.py       # LOW/MEDIUM/HIGH/CRITICAL with individual signals
│   │   ├── recommendation.py    # BUY/WATCH/HOLD/SELL/AVOID with reasons & risks
│   │   └── engine.py            # AnalyticsEngine coordinator
│   │
│   ├── integrations/            # External APIs
│   │   ├── base.py              # SorareProvider, NewsProvider, PredictionProvider
│   │   └── sorare/
│   │       ├── client.py        # Production GraphQL client (retries, timeouts, cache)
│   │       ├── websocket.py     # ActionCable WebSocket subscriber
│   │       └── queries/         # Reusable GraphQL queries
│   │
│   ├── workers/                 # Background tasks
│   │   ├── sync_worker.py       # 30-minute periodic data sync
│   │   └── websocket_worker.py  # Real-time WebSocket subscriber
│   │
│   └── utils/
│       ├── redis_client.py      # Async Redis with in-memory fallback
│       ├── security.py          # Bcrypt hashing & JWT token handling
│       ├── logger.py            # Structured JSON logger with secret redaction
│       └── seed.py              # Realistic 52-player demo seed generator
│
├── tests/                       # Pytest test suite
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_analytics.py
│   ├── test_api_endpoints.py
│   ├── test_auth.py
│   └── test_sorare_client.py
│
├── migrations/                  # Alembic database migrations
├── docker/
│   └── entrypoint.sh            # Container startup script
├── Dockerfile                   # Multi-stage production container
├── docker-compose.yml           # Compose stack (api, worker, postgres, redis)
├── requirements.txt             # Python production dependencies
└── .env.example                 # Example environment variables
```

---

## 3. Getting Started

### Option A: Docker Compose (Production Setup)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Start the full stack:
   ```bash
   docker compose up -d
   ```

3. Verify services:
   ```bash
   curl http://localhost:8000/health
   ```
   Open API documentation in your browser:
   [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option B: Local Python Development

1. Create and activate a Python 3.12+ virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Seed the local database (works with SQLite out of the box):
   ```bash
   python -m app.utils.seed
   ```

4. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 4. Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | Runtime environment (`development`, `production`, `test`) |
| `DEBUG` | `true` | Enable debug logs |
| `SECRET_KEY` | `scoutlab-secret...` | Minimum 32-character secret for JWT signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT expiration in minutes (24h) |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins for the Lovable frontend |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching & locking instance |
| `DEMO_MODE` | `true` | Auto-seed realistic dataset if database is empty |
| `SORARE_GRAPHQL_URL` | `https://api.sorare.com/federation/graphql` | Official Sorare GraphQL endpoint |
| `SORARE_WS_URL` | `wss://ws.sorare.com/cable` | Official Sorare WebSocket endpoint |
| `SORARE_API_KEY` | `""` | Optional Sorare API Key |
| `SORARE_JWT` | `""` | Optional Sorare JWT |
| `FORM_WEIGHT` | `0.25` | Scout score weight for recent form |
| `CONSISTENCY_WEIGHT` | `0.15` | Scout score weight for score variance |
| `MINUTES_WEIGHT` | `0.15` | Scout score weight for match minutes |
| `FIXTURE_WEIGHT` | `0.15` | Scout score weight for schedule difficulty |
| `AVAILABILITY_WEIGHT` | `0.15` | Scout score weight for fitness/suspensions |
| `MARKET_WEIGHT` | `0.15` | Scout score weight for price valuation |
| `SYNC_INTERVAL_MINUTES` | `30` | Periodic background reconciliation cadence |

---

## 5. Analytics & Scouting Engine

ScoutLab uses **fully deterministic and explainable metrics** rather than black-box models.

### Sub-Scores (0 to 100)
1. **Form Score**: Recency-weighted moving average over the last 5 appearances.
2. **Consistency Score**: Measures variance / standard deviation in match points.
3. **Minutes Score**: Percentage of available 90-minute periods completed.
4. **Fixture Score**: Difficulty rating of upcoming 3 opponents (with home advantage bonus).
5. **Availability Score**: 100 (fit), 40 (doubtful), 0 (confirmed OUT or suspended).
6. **Market Score**: Ratio of current card floor to the 30-day baseline average.

### Composite Scout Score (0–100)
$$\text{Scout Score} = \sum (\text{SubScore}_i \times \text{Weight}_i)$$
Weights are completely configurable via environment variables.

### Starting XI Probability
Deterministic starting probability (0–100%) clearly stamped as:
```json
{
  "starting_probability": 92.0,
  "label": "PREDICTION",
  "confidence": 85.0,
  "expected_role": "Starter",
  "factors": ["Started 5 of last 5 matches.", "Averaging 80+ minutes per appearance."]
}
```

### Risk Engine & Classification
Classifies player risks into `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` with individual signals:
- Medical reports & active injuries
- Disciplinary suspensions
- Low recent playing time / substitute usage
- Severe form slumps
- Hostile upcoming match runs
- Negative price momentum

### Recommendations
`BUY`, `WATCH`, `HOLD`, `SELL`, `AVOID` generated with explicit reasons, risks, and confidence ratings.

---

## 6. Seed Dataset

With `DEMO_MODE=true` (enabled by default), ScoutLab seeds:
- **52 Real European Football Stars**: Mbappé, Haaland, Vinicius Jr, Bellingham, Saka, De Bruyne, Rodri, Kane, Musiala, Saliba, Courtois, Donnarumma, Ter Stegen, etc.
- **Top European Clubs**: Real Madrid, Manchester City, Arsenal, Bayern Munich, PSG, Barcelona, Inter Milan, Liverpool, Bayer Leverkusen, Atletico Madrid.
- **Competitions**: Premier League, La Liga, UEFA Champions League, Bundesliga, Serie A.
- **SO5 Gameweeks**: Current opened GW 502, upcoming GW 503, completed GW 501.
- **Match scores, card inventories, 30-day price histories, active injuries, alerts, and news articles**.

Default Demo Credentials:
- **Username**: `ScoutMaster_Alpha`
- **Email**: `admin@scoutlab.io`
- **Password**: `password123`

---

## 7. Running Tests

Run the complete test suite:
```bash
pytest -v tests/
```

Test coverage includes:
- Models & Foreign Key constraints
- Repositories & filtering
- Analytics formulas & edge cases
- Starting XI prediction & risk engine
- Authentication & JWT issuance
- Sorare GraphQL client mocked retries & timeouts
- REST API v1 endpoints
