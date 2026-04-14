FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости системы для asyncpg
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Добавляем корень проекта в PYTHONPATH
ENV PYTHONPATH=/app/src

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY src/ ./src/
COPY scripts/ ./scripts/

# Команда запуска
CMD ["python", "src/main.py"]