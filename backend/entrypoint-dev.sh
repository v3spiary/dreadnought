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
python manage.py init_tracker --username admin

# curl -X PUT "opensearch:9200/tracker_metrics" -H 'Content-Type: application/json' -d'
# {
#   "mappings": {
#     "properties": {
#       "date": {"type": "date"},
#       "user_id": {"type": "keyword"},
#       "calories": {"type": "float"},
#       "steps": {"type": "long"}
#     }
#   },
#   "settings": {"refresh_interval": "1s"}
# }'

exec uvicorn config.asgi-dev:application \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
