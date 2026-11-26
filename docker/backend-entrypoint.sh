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
  if [ "${DOCS_HOST_REQUIRED:-0}" = 1 ]; then
    ruby -rjson -e '
      path = "/app/backend/storage/makedocs/filesystem/host/ready.json"
      deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + 40
      loop do
        ready = !File.symlink?(path) && File.file?(path) && (Time.now.to_f - JSON.parse(File.read(path)).fetch("at") < 10) rescue false
        break if ready
        abort "Host filesystem adapter unavailable: launch with python3 tools/init_dev_env.py up" if Process.clock_gettime(Process::CLOCK_MONOTONIC) >= deadline
        sleep 0.2
      end'
  fi
  # Compose gates this on PostgreSQL readiness; any preparation error is fatal.
  bundle exec rails db:prepare catalog:sync
fi
exec "$@"
