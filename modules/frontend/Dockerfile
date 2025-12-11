# Build stage
FROM node:18-alpine as build-stage

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build application with increased memory
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

# Production stage
FROM nginx:1.21-alpine as production-stage

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 