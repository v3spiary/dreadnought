# STAGE 1: CHECK & BUILD BUNDLE
FROM node:20-alpine AS frontend

WORKDIR /app

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ARG VITE_WS_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build

# STAGE 2: SETUP PYTHON ENV
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libjpeg-dev \ 
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libtk8.6 \
    libtcl8.6 \
    python3-dev \
    make \
    cmake \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app

COPY backend/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd -g 1000 deadwood && useradd -u 1000 -g deadwood -m deadwood

# STAGE 3: DRF REST API
FROM base AS server

RUN mkdir -p /app/frontend_dist

RUN mkdir -p /app/config/static

COPY --from=frontend /app/dist /app/frontend_dist

COPY backend/entrypoint.sh .

RUN chmod +x entrypoint.sh

COPY backend/ /app/

EXPOSE 8000

RUN chown -R deadwood:deadwood /app

USER deadwood

ENTRYPOINT ["sh", "./entrypoint.sh"]

# STAGE 4: CELERY WORKER
FROM base AS worker

COPY backend/ /app/

RUN chown -R deadwood:deadwood /app

USER deadwood

ENTRYPOINT celery -A config worker --loglevel=info --concurrency=4

# STAGE 5: CELERY BEAT
FROM worker AS beat 

ENTRYPOINT celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
