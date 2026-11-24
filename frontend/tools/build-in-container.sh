#!/bin/sh
set -eu

# Build in the existing container without touching the live server's .next cache.
test -d /app/frontend/node_modules/next
build_dir=$(mktemp -d /tmp/engineering-library-build.XXXXXX)
trap 'rm -rf "$build_dir"' EXIT HUP INT TERM
tar --exclude='./node_modules' --exclude='./.next' --exclude='./*.tsbuildinfo' -cf "$build_dir/source.tar" .
tar -xf "$build_dir/source.tar" -C "$build_dir"
rm "$build_dir/source.tar"
ln -s /app/frontend/node_modules "$build_dir/node_modules"
cd "$build_dir"
npm run build
