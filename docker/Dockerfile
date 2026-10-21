# syntax=docker/dockerfile:1

FROM ruby:3.4.11-bookworm AS backend-dependencies
WORKDIR /app/backend
ENV BUNDLE_PATH=/usr/local/bundle \
    BUNDLE_APP_CONFIG=/tmp/bundle-config \
    BUNDLE_FROZEN=true
COPY backend/Gemfile backend/Gemfile.lock ./
RUN bundle install && bundle clean --force

FROM backend-dependencies AS backend-development
ENV RAILS_ENV=development HOME=/tmp
COPY --chown=1000:1000 backend/ ./
RUN mkdir -p tmp/pids log && chown -R 1000:1000 /app/backend
COPY --chmod=755 docker/backend-entrypoint.sh /usr/local/bin/backend-entrypoint
USER 1000:1000
EXPOSE 3000
ENTRYPOINT ["backend-entrypoint"]
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0", "-p", "3000"]

FROM node:24.22.0-bookworm-slim AS frontend-dependencies
# Image dependency target remains independent of development bind-mount installs.
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci && npm cache clean --force

FROM frontend-dependencies AS frontend-development
# Browser tooling belongs only to the development target.
USER root
ENV PLAYWRIGHT_MODULE=/opt/browser/node_modules/playwright \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
RUN npm install --prefix /opt/browser --save-exact playwright@1.58.2 \
    && /opt/browser/node_modules/.bin/playwright install --with-deps chromium \
    && chmod -R a+rX /opt/browser /opt/playwright \
    && npm cache clean --force
ENV HOME=/tmp npm_config_cache=/tmp/npm-cache
WORKDIR /app/frontend
COPY --chown=1000:1000 frontend/ ./
RUN chown 1000:1000 /app/frontend
COPY --chmod=755 docker/frontend-entrypoint.sh /usr/local/bin/frontend-entrypoint
USER 1000:1000
EXPOSE 3000
ENTRYPOINT ["frontend-entrypoint"]
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
