#!/bin/sh
set -eu

# This entrypoint belongs only to frontend-development. npm ci replaces any stale
# host packages with the locked Linux dependencies inside the source bind mount.
npm ci --include=dev
exec "$@"
