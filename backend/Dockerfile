FROM ruby:3.4.11-bookworm
WORKDIR /app
ENV BUNDLE_PATH=/app/vendor/bundle BUNDLE_APP_CONFIG=/tmp/bundle-config
COPY Gemfile Gemfile.lock ./
RUN bundle install
COPY . .
CMD ["sh", "-c", "set -e; bundle check || bundle install; exec bundle exec rails server -b 0.0.0.0 -p 3000"]
