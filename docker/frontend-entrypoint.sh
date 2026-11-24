#!/bin/sh
set -eu

# Cache metadata lives with the disposable dependencies, never in configuration.
# Include the hidden npm lock to invalidate installs performed by the host.
dependency_fingerprint() {
  node - <<'JS'
const fs = require('node:fs');
const crypto = require('node:crypto');
const hash = crypto.createHash('sha256');
hash.update(JSON.stringify([process.version, process.platform, process.arch]));
for (const file of ['package.json', 'package-lock.json', process.env.ENTRYPOINT_SOURCE, 'node_modules/.package-lock.json']) {
  hash.update(file);
  hash.update(fs.existsSync(file) ? fs.readFileSync(file) : 'missing');
}
console.log(hash.digest('hex'));
JS
}
export ENTRYPOINT_SOURCE="$0"
cache_file=node_modules/.engineering-library-dependencies
fingerprint=$(dependency_fingerprint)
cached=$(cat "$cache_file" 2>/dev/null || true)
if [ "$fingerprint" = "$cached" ] && npm ls --all --include=dev --silent >/dev/null 2>&1 &&
  node -e 'require("sharp"); require("next/dist/build/swc").loadBindings().catch(() => process.exit(1))'; then
  echo 'Locked development dependencies verified; reusing installed packages.'
else
  npm ci --include=dev
  dependency_fingerprint > "$cache_file"
fi
exec "$@"
