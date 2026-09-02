#!/bin/sh
set -e

echo "Waiting for database to be ready..."
# Run database migrations
echo "Applying database migrations..."
alembic upgrade head || echo "Migration skipped or completed."

# If DEMO_MODE is true, seed data
if [ "$DEMO_MODE" = "true" ]; then
    echo "DEMO_MODE=true: Ensuring database has seed data..."
    python -m app.utils.seed || echo "Seed finished or already populated."
fi

echo "Starting server: $@"
exec "$@"
