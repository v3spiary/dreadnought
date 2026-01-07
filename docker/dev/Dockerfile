# STAGE 1: CHECK & BUILD BUNDLE
FROM node:20-alpine AS frontend

WORKDIR /app

COPY frontend/package*.json ./

RUN npm i

COPY frontend/ .

ENTRYPOINT [ "npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173" ]

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
    git \
    vim \
    postgresql-client \
    telnet \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app

COPY backend/requirements.txt /app/

COPY docker/dev/requirements.txt /app/requirements-dev.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir -r requirements-dev.txt

RUN pip install --no-cache-dir debugpy

RUN groupadd -g 1000 deadwood && useradd -u 1000 -g deadwood -m deadwood

# STAGE 3: DEV SERVER
FROM base AS dev-server

RUN mkdir -p /app/config/static

COPY backend/ /app/

RUN chmod +x entrypoint-dev.sh

EXPOSE 8000 5678 5679

RUN chown -R deadwood:deadwood /app

USER deadwood

ENTRYPOINT ["sh", "./entrypoint-dev.sh"]

# STAGE 4: DEV CELERY WORKER
FROM base AS dev-worker

COPY backend/ /app/

ENV PYTHONBREAKPOINT=debugpy.breakpoint

ENV DJANGO_SETTINGS_MODULE=config.dev

RUN chown -R deadwood:deadwood /app

USER deadwood

EXPOSE 5680

CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5680", "--wait-for-client", "-m celery", "-A", "config", "worker", "--loglevel=info", "--concurrency=2", "-E"]

# STAGE 5: DEV CELERY BEAT
FROM dev-worker AS dev-beat

EXPOSE 5681

CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5681", "--wait-for-client", "-m celery", "-A", "config", "beat", "--loglevel=info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
