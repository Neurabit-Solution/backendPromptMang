#!/bin/sh
# =============================================================================
# Docker / production entrypoint
# =============================================================================
# This script runs every time the container starts.
# It applies any pending Alembic migrations first, then starts the API server.
#
# WHY run migrations here instead of a separate CI step?
# - On first deploy of a new release, the migration and the code ship together.
# - Rolling restarts are safe: Alembic is idempotent — if the migration was
#   already applied (alembic_version table is up to date), `upgrade head` is
#   a no-op and exits in milliseconds.
# - Keeps the deploy process simple: one artifact, one entrypoint.
# =============================================================================
set -e  # Exit immediately if any command returns a non-zero status

echo "================================================="
echo " MagicPic API — Starting up"
echo "================================================="

echo "[1/2] Running Alembic migrations..."
alembic upgrade head
echo "      Migrations complete."

echo "[2/2] Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
