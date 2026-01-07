.PHONY: up down logs backend frontend celery test debug

up:
	docker-compose -f docker-compose/docker-compose-dev.yml up -d --build

down:
	docker-compose -f docker-compose/docker-compose-dev.yml down -v

logs:
	docker-compose -f docker-compose/docker-compose-dev.yml logs -f

backend-logs:
	docker-compose -f docker-compose/docker-compose-dev.yml logs -f backend

frontend-logs:
	docker-compose -f docker-compose/docker-compose-dev.yml logs -f frontend

celery-logs:
	docker-compose -f docker-compose/docker-compose-dev.yml logs -f celery

backend:
	docker-compose -f docker-compose/docker-compose-dev.yml exec backend bash

frontend:
	docker-compose -f docker-compose/docker-compose-dev.yml exec frontend sh

db:
	docker-compose -f docker-compose/docker-compose-dev.yml exec db psql -U postgres deadwood_dev

test:
	docker-compose -f docker-compose/docker-compose-dev.yml exec backend pytest -v

test-debug:
	docker-compose -f docker-compose/docker-compose-dev.yml run --rm -p 5679:5679 backend \
		python -m debugpy --listen 0.0.0.0:5679 --wait-for-client -m pytest

migrate:
	docker-compose -f docker-compose/docker-compose-dev.yml exec backend python manage.py migrate

shell:
	docker-compose -f docker-compose/docker-compose-dev.yml exec backend python manage.py shell_plus

attach-django:
	docker-compose -f docker-compose/docker-compose-dev.yml exec -d backend \
		python -m debugpy --listen 0.0.0.0:5678 --wait-for-client manage.py runserver 0.0.0.0:8000

attach-celery:
	docker-compose -f docker-compose/docker-compose-dev.yml exec -d celery \
		python -m debugpy --listen 0.0.0.0:5680 --wait-for-client -m celery -A config worker -l info

build:
	docker-compose -f docker-compose/docker-compose-dev.yml build

rebuild:
	docker-compose -f docker-compose/docker-compose-dev.yml build --no-cache

rebuild-frontend:
	docker-compose -f docker-compose/docker-compose-dev.yml build --no-cache frontend
