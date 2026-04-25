"""initial schema

Revision ID: b769f946a353
Revises:
Create Date: 2026-04-14 15:15:55.655908

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b769f946a353"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.execute("""
               CREATE TABLE IF NOT EXISTS users
               (
                   user_id BIGINT PRIMARY KEY,
                   username TEXT,
                   created_at TEXT NOT NULL
               )
               """)

    # user_cards
    op.execute("""
               CREATE TABLE IF NOT EXISTS user_cards
               (
                   user_id BIGINT PRIMARY KEY,
                   last_card_date TEXT NOT NULL,
                   total_cards INTEGER DEFAULT 0,
                   upright_count INTEGER DEFAULT 0,
                   reversed_count INTEGER DEFAULT 0
               )
               """)

    # card_back
    op.execute("""
               CREATE TABLE IF NOT EXISTS card_back
               (
                   id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                   file_id TEXT NOT NULL
               )
               """)

    # tarot_cards
    op.execute("""
               CREATE TABLE IF NOT EXISTS tarot_cards
               (
                   id INTEGER PRIMARY KEY,
                   name TEXT NOT NULL,
                   arcana TEXT,
                   suit TEXT,
                   card_number TEXT,
                   file_id TEXT,
                   description TEXT,
                   meaning_direct TEXT,
                   meaning_reversed TEXT,
                   detailed_direct TEXT,
                   detailed_reversed TEXT
               )
               """)

    # user_card_history
    op.execute("""
               CREATE TABLE IF NOT EXISTS user_card_history
               (
                   id SERIAL PRIMARY KEY,
                   user_id BIGINT NOT NULL,
                   card_id INTEGER NOT NULL,
                   opened_at TIMESTAMP DEFAULT NOW
               (
               )
                   )
               """)

    op.execute("""
               CREATE INDEX IF NOT EXISTS idx_user_card_history_user_id
                   ON user_card_history (user_id, opened_at DESC)
               """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_user_card_history_user_id")
    op.execute("DROP TABLE IF EXISTS user_card_history")
    op.execute("DROP TABLE IF EXISTS tarot_cards")
    op.execute("DROP TABLE IF EXISTS card_back")
    op.execute("DROP TABLE IF EXISTS user_cards")
    op.execute("DROP TABLE IF EXISTS users")
