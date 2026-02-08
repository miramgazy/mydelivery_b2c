# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (включая для Pillow/ImageField)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директории для статических и медиа файлов
RUN mkdir -p /app/staticfiles /app/media

# Копируем и делаем исполняемым entrypoint скрипты
COPY docker-entrypoint.sh /app/
COPY docker-entrypoint-coolify.sh /app/
RUN chmod +x /app/docker-entrypoint.sh /app/docker-entrypoint-coolify.sh

# Открываем порт
EXPOSE 8000

# Запускаем через entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]