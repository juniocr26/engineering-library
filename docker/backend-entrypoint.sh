#!/bin/sh
set -eu

# Compose development installs into the source bind mount, hidden from image gems.
if ! bundle check; then
  if [ "${RAILS_ENV:-}" != development ]; then
    exit 1
  fi
  bundle install
  bundle check
fi
if [ "${1:-}" = bundle ] && [ "${2:-}" = exec ] && [ "${3:-}" = rails ] && [ "${4:-}" = server ]; then
  mkdir -p tmp/pids
  rm -f tmp/pids/server.pid
  # Compose gates this on PostgreSQL readiness; any preparation error is fatal.
  bundle exec rails db:prepare catalog:sync
fi
exec "$@"
