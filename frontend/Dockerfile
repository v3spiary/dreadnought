# STAGE 1: CHECK & BUILD BUNDLE
FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ARG VITE_WS_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL

COPY package*.json ./

RUN npm ci

COPY . .

# RUN npm run lint

# RUN npm audit --audit-level=high

RUN npm run build

# STAGE 2: RUN BUNDLE
FROM nginx:alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
