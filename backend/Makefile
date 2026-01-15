.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test clean prod-build prod-up prod-logs ssl-init logs-nginx logs-frontend

help:
	@echo "Доступные команды:"
	@echo "  make build          - Собрать Docker образы (Dev)"
	@echo "  make up             - Запустить все сервисы (Dev)"
	@echo "  make down           - Остановить все сервисы"
	@echo "  make restart        - Перезапустить все сервисы"
	@echo "  make logs           - Показать логи всех сервисов"
	@echo "  make logs-backend   - Показать логи backend"
	@echo "  make logs-frontend  - Показать логи frontend"
	@echo "  make logs-nginx     - Показать логи nginx"
	@echo "  make logs-celery    - Показать логи celery"
	@echo "  make shell          - Открыть Django shell"
	@echo "  make bash           - Открыть bash в backend контейнере"
	@echo "  make migrate        - Применить миграции"
	@echo "  make makemigrations - Создать миграции"
	@echo "  make createsuperuser - Создать суперпользователя"
	@echo "  make collectstatic  - Собрать статические файлы"
	@echo "  make test           - Запустить тесты"
	@echo "  make clean          - Остановить и удалить контейнеры"
	@echo "  make clean-all      - Остановить и удалить контейнеры с volumes"
	@echo "  --- Production ---"
	@echo "  make prod-build     - Собрать Production образы"
	@echo "  make prod-up        - Запустить Production"
	@echo "  make prod-down      - Остановить Production"
	@echo "  make prod-logs      - Логи Production"
	@echo "  make ssl-init       - Получить SSL сертификат (Certbot)"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-nginx:
	docker-compose logs -f nginx

logs-celery:
	docker-compose logs -f celery

shell:
	docker-compose exec backend python manage.py shell

bash:
	docker-compose exec backend /bin/bash

migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

collectstatic:
	docker-compose exec backend python manage.py collectstatic --noinput

test:
	docker-compose exec backend pytest

clean:
	docker-compose down

clean-all:
	docker-compose down -v

# Инициализация проекта (Dev)
init: build up migrate createsuperuser
	@echo "Проект инициализирован!"
	@echo "Backend доступен на http://localhost/api/"
	@echo "Frontend доступен на http://localhost/"

# Полная пересборка (Dev)
rebuild: clean-all build up migrate
	@echo "Проект пересобран!"

# --- Production ---

prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

ssl-init:
	@read -p "Enter domain (e.g., example.com): " domain; \
	read -p "Enter email: " email; \
	docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
		--webroot \
		--webroot-path=/var/www/certbot \
		--email $$email \
		--agree-tos \
		--no-eff-email \
		-d $$domain -d www.$$domain