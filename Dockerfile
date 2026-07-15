FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Добавляем и корень проекта (/app), и папку с кодом (/app/src) в PYTHONPATH.
# Это позволит Python видеть как nexus_sdk в корне, так и модули бота в src/.
ENV PYTHONPATH=/app:/app/src

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- ИСПРАВЛЕНИЕ: Копируем локальный пакет SDK ---
COPY nexus_sdk/ ./nexus_sdk/

# Копируем код, скрипты и файл конфигурации Alembic
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY alembic.ini .

# Команда запуска
CMD ["python", "src/main.py"]