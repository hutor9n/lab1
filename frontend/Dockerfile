# -------------------------------------------------------------------
# Stage 1: Build React SPA application
# -------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# -------------------------------------------------------------------
# Stage 2: Serve production bundle with Nginx
# -------------------------------------------------------------------
FROM nginx:alpine

ENV API_UPSTREAM=lab-api:8000
COPY frontend/nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
