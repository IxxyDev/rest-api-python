#!/bin/sh
set -e

if [ -z "$API_KEY" ]; then
  echo "ERROR: API_KEY env variable must be provided" >&2
  exit 1
fi

alembic upgrade head

if [ "$SEED_DATABASE" = "true" ]; then
  python -m app.seeds
fi

exec "$@"
