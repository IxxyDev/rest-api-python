#!/bin/sh
set -e

alembic upgrade head

if [ "$SEED_DATABASE" = "true" ]; then
  python -m app.seeds
fi

exec "$@"
