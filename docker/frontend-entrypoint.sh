#!/bin/sh
set -eu

# A bind-mounted lockfile may have changed since this image was built.
node -e '
const fs = require("node:fs");
for (const file of ["package.json", "package-lock.json"]) {
  if (!fs.readFileSync("/app/" + file).equals(fs.readFileSync(file))) {
    console.error(file + " changed: rebuild with docker compose up -d --build");
    process.exit(1);
  }
}
'
exec "$@"
