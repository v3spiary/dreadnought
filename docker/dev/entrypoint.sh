#!/bin/sh

echo "DB not yet run..."

while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done

echo "DB did run."

python3 manage.py collectstatic --no-input
python3 manage.py makemigrations --no-input
python3 manage.py migrate --no-input
python3 manage.py initdb

# exec uvicorn config.asgi:application \
#   --host 0.0.0.0 \
#   --port 8000

python3 -m debugpy --listen 0.0.0.0:5678 --wait-for-client uvicorn config.asgi-dev:application --host 0.0.0.0 --port 8000 --reload

# python3 -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn config.asgi-dev:application --host 0.0.0.0 --port 8000 --no-reload
