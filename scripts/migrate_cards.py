import sqlite3
from pathlib import Path

import psycopg2

# Подключаемся к SQLite (старая БД)
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "src" / "database" / "db.db"

# Подключаемся к SQLite по абсолютному пути
sqlite_conn = sqlite3.connect(DB_PATH)
sqlite_cur = sqlite_conn.cursor()

# Загружаем карты из SQLite
sqlite_cur.execute("""
    SELECT id, name, arcana, suit, card_number, file_id,
           description, meaning_direct, meaning_reversed,
           detailed_direct, detailed_reversed
    FROM tarot_cards
""")
cards = sqlite_cur.fetchall()
print(f"📖 Найдено {len(cards)} карт в SQLite")

# Подключаемся к PostgreSQL
pg_conn = psycopg2.connect("postgresql://bot_user:bot_pass@82.25.185.72:5432/tarot_bot")
pg_cur = pg_conn.cursor()

# Очищаем таблицу
pg_cur.execute("TRUNCATE tarot_cards;")
print("🧹 Таблица очищена")

# Вставляем данные
for card in cards:
    pg_cur.execute(
        """
        INSERT INTO tarot_cards
        (id, name, arcana, suit, card_number, file_id, description,
         meaning_direct, meaning_reversed, detailed_direct, detailed_reversed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        card,
    )

pg_conn.commit()
print("💾 Данные сохранены")

# Проверяем
pg_cur.execute("SELECT COUNT(*) FROM tarot_cards")
count = pg_cur.fetchone()[0]
print(f"✅ В PostgreSQL {count} карт")

pg_cur.close()
pg_conn.close()
sqlite_conn.close()
