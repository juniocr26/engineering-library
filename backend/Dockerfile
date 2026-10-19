FROM ruby:3.4.11-bookworm
WORKDIR /app
ENV BUNDLE_PATH=/app/vendor/bundle BUNDLE_APP_CONFIG=/tmp/bundle-config
COPY Gemfile Gemfile.lock ./
RUN bundle install
COPY . .
# The development bind mount can retain a PID from a previous container.
CMD ["sh", "-c", "set -e; bundle check || bundle install; rm -f tmp/pids/server.pid; exec bundle exec rails server -b 0.0.0.0 -p 3000"]
