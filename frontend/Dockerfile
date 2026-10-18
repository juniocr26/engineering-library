FROM node:24.22.0-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
CMD ["sh", "-c", "npm ci && exec npm run dev -- --hostname 0.0.0.0"]
