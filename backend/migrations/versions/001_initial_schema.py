"""Initial schema for ScoutLab

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-02 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Clubs
    op.create_table(
        "clubs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("short_name", sa.String(64), nullable=True),
        sa.Column("logo_url", sa.String(512), nullable=True),
        sa.Column("country", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_clubs_slug", "clubs", ["slug"])
    op.create_index("ix_clubs_sorare_id", "clubs", ["sorare_id"])

    # Competitions
    op.create_table(
        "competitions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_competitions_slug", "competitions", ["slug"])
    op.create_index("ix_competitions_sorare_id", "competitions", ["sorare_id"])

    # Players
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("slug", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(64), nullable=False),
        sa.Column("active_club_id", sa.Integer(), sa.ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nationality", sa.String(128), nullable=True),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_players_display_name", "players", ["display_name"])
    op.create_index("ix_players_position", "players", ["position"])
    op.create_index("ix_players_age", "players", ["age"])
    op.create_index("ix_players_slug", "players", ["slug"])
    op.create_index("ix_players_sorare_id", "players", ["sorare_id"])
    op.create_index("ix_players_active_club_id", "players", ["active_club_id"])
    op.create_index("ix_players_pos_club", "players", ["position", "active_club_id"])

    # Games
    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("home_club_id", sa.Integer(), sa.ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("away_club_id", sa.Integer(), sa.ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("competition_id", sa.Integer(), sa.ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(64), nullable=False, server_default="SCHEDULED"),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("minute", sa.Integer(), nullable=True),
        sa.Column("coverage_status", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_games_date", "games", ["date"])
    op.create_index("ix_games_status", "games", ["status"])
    op.create_index("ix_games_home_club_id", "games", ["home_club_id"])
    op.create_index("ix_games_away_club_id", "games", ["away_club_id"])
    op.create_index("ix_games_competition_id", "games", ["competition_id"])
    op.create_index("ix_games_date_status", "games", ["date", "status"])

    # Player Game Scores
    op.create_table(
        "player_game_scores",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("average_score", sa.Float(), nullable=True),
        sa.Column("projected_score", sa.Float(), nullable=True),
        sa.Column("projection_grade", sa.String(32), nullable=True),
        sa.Column("projection_reliability", sa.Float(), nullable=True),
        sa.Column("decisive_score", sa.Float(), nullable=True),
        sa.Column("all_around_score", sa.Float(), nullable=True),
        sa.Column("score_status", sa.String(64), nullable=True),
        sa.Column("scoring_version", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_player_game_scores_player_id", "player_game_scores", ["player_id"])
    op.create_index("ix_player_game_scores_game_id", "player_game_scores", ["game_id"])
    op.create_index("ix_player_game_scores_score", "player_game_scores", ["score"])
    op.create_index("ix_scores_player_game", "player_game_scores", ["player_id", "game_id"])

    # Score Snapshots
    op.create_table(
        "score_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("l5_average", sa.Float(), nullable=True),
        sa.Column("l15_average", sa.Float(), nullable=True),
        sa.Column("l40_average", sa.Float(), nullable=True),
        sa.Column("clean_sheet_rate", sa.Float(), nullable=True),
        sa.Column("goal_rate", sa.Float(), nullable=True),
        sa.Column("assist_rate", sa.Float(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_score_snapshots_player_id", "score_snapshots", ["player_id"])
    op.create_index("ix_score_snapshots_observed_at", "score_snapshots", ["observed_at"])

    # Injuries
    op.create_table(
        "injuries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("kind", sa.String(128), nullable=False),
        sa.Column("details", sa.String(512), nullable=True),
        sa.Column("status", sa.String(64), nullable=False, server_default="OUT"),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expected_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_injuries_player_id", "injuries", ["player_id"])
    op.create_index("ix_injuries_active", "injuries", ["active"])
    op.create_index("ix_injuries_player_active", "injuries", ["player_id", "active"])

    # Suspensions
    op.create_table(
        "suspensions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("competition", sa.String(128), nullable=True),
        sa.Column("kind", sa.String(128), nullable=False),
        sa.Column("reason", sa.String(512), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("matches", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_suspensions_player_id", "suspensions", ["player_id"])
    op.create_index("ix_suspensions_active", "suspensions", ["active"])
    op.create_index("ix_suspensions_player_active", "suspensions", ["player_id", "active"])

    # Cards
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("asset_id", sa.String(128), nullable=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("rarity", sa.String(64), nullable=False),
        sa.Column("position", sa.String(64), nullable=True),
        sa.Column("power", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("grade", sa.String(32), nullable=True),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_cards_player_id", "cards", ["player_id"])
    op.create_index("ix_cards_season_year", "cards", ["season_year"])
    op.create_index("ix_cards_rarity", "cards", ["rarity"])

    # Card Prices
    op.create_table(
        "card_prices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("card_id", sa.Integer(), sa.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(16), nullable=False, server_default="EUR"),
        sa.Column("source", sa.String(64), nullable=False, server_default="secondary_market"),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_card_prices_card_id", "card_prices", ["card_id"])
    op.create_index("ix_card_prices_observed_at", "card_prices", ["observed_at"])
    op.create_index("ix_card_prices_card_observed", "card_prices", ["card_id", "observed_at"])

    # Price Snapshots
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("card_id", sa.Integer(), sa.ForeignKey("cards.id", ondelete="SET NULL"), nullable=True),
        sa.Column("average_price", sa.Float(), nullable=False),
        sa.Column("lowest_ask", sa.Float(), nullable=True),
        sa.Column("highest_bid", sa.Float(), nullable=True),
        sa.Column("volume_24h", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(16), nullable=False, server_default="EUR"),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_price_snapshots_player_id", "price_snapshots", ["player_id"])
    op.create_index("ix_price_snapshots_observed_at", "price_snapshots", ["observed_at"])
    op.create_index("ix_price_snapshots_player_observed", "price_snapshots", ["player_id", "observed_at"])

    # SO5 Fixtures
    op.create_table(
        "so5_fixtures",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sorare_id", sa.String(128), nullable=True, unique=True),
        sa.Column("event", sa.String(64), nullable=True, server_default="football"),
        sa.Column("event_name", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=True),
        sa.Column("game_week", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cutoff_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("state", sa.String(32), nullable=False, server_default="upcoming"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_so5_fixtures_game_week", "so5_fixtures", ["game_week"])
    op.create_index("ix_so5_fixtures_state", "so5_fixtures", ["state"])
    op.create_index("ix_so5_fixtures_gw_state", "so5_fixtures", ["game_week", "state"])

    # Player Metrics
    op.create_table(
        "player_metrics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("form_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("consistency_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("minutes_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("fixture_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("market_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("availability_score", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("scout_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("risk_level", sa.String(32), nullable=False, server_default="LOW"),
        sa.Column("starting_probability", sa.Float(), nullable=False, server_default="50.0"),
        sa.Column("recommendation", sa.String(32), nullable=False, server_default="HOLD"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="70.0"),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_player_metrics_player_id", "player_metrics", ["player_id"])
    op.create_index("ix_player_metrics_scout_score", "player_metrics", ["scout_score"])
    op.create_index("ix_player_metrics_recommendation", "player_metrics", ["recommendation"])
    op.create_index("ix_player_metrics_starting_probability", "player_metrics", ["starting_probability"])
    op.create_index("ix_metrics_scout_rec", "player_metrics", ["scout_score", "recommendation"])

    # News
    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("category", sa.String(64), nullable=False, server_default="general"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(32), nullable=False, server_default="REPORT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_news_published_at", "news", ["published_at"])
    op.create_index("ix_news_category", "news", ["category"])

    # News Player Links
    op.create_table(
        "news_player_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("news_id", sa.Integer(), sa.ForeignKey("news.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_news_player", "news_player_links", ["news_id", "player_id"], unique=True)

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("group_name", sa.String(128), nullable=True, server_default="ScoutLab Alpha Syndicate"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    # Watchlists
    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_price", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_watchlists_user_id", "watchlists", ["user_id"])
    op.create_index("ix_watchlists_player_id", "watchlists", ["player_id"])
    op.create_index("ix_watchlist_user_player", "watchlists", ["user_id", "player_id"], unique=True)

    # Alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(64), nullable=False, server_default="PRICE_DROP"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False, server_default="INFO"),
        sa.Column("source_type", sa.String(32), nullable=False, server_default="FACT"),
        sa.Column("read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alerts_user_id", "alerts", ["user_id"])
    op.create_index("ix_alerts_player_id", "alerts", ["player_id"])
    op.create_index("ix_alerts_read", "alerts", ["read"])
    op.create_index("ix_alerts_user_read", "alerts", ["user_id", "read"])

    # Sync Status
    op.create_table(
        "sync_status",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_name", sa.String(128), nullable=False, unique=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="IDLE"),
        sa.Column("last_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sync_status_job_name", "sync_status", ["job_name"])


def downgrade() -> None:
    op.drop_table("sync_status")
    op.drop_table("alerts")
    op.drop_table("watchlists")
    op.drop_table("users")
    op.drop_table("news_player_links")
    op.drop_table("news")
    op.drop_table("player_metrics")
    op.drop_table("so5_fixtures")
    op.drop_table("price_snapshots")
    op.drop_table("card_prices")
    op.drop_table("cards")
    op.drop_table("suspensions")
    op.drop_table("injuries")
    op.drop_table("score_snapshots")
    op.drop_table("player_game_scores")
    op.drop_table("games")
    op.drop_table("players")
    op.drop_table("competitions")
    op.drop_table("clubs")
