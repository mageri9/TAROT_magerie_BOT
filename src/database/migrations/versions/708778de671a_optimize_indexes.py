"""optimize_indexes

Revision ID: 708778de671a
Revises: b769f946a353
Create Date: 2026-04-25 16:14:55.287354

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "708778de671a"
down_revision: Union[str, Sequence[str], None] = "b769f946a353"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
transactional = True


def upgrade() -> None:
    """Добавляем оптимизированные индексы."""

    # Удаляем старый индекс
    op.drop_index("idx_user_card_history_user_id", table_name="user_card_history")

    # Покрывающий индекс для истории карт
    op.create_index(
        "idx_user_card_history_covering",
        "user_card_history",
        ["user_id", sa.text("opened_at DESC")],
        postgresql_include=["card_id"],
    )

    # Индекс для подсчёта активных пользователей
    op.create_index("idx_user_cards_last_date", "user_cards", ["last_card_date"])


def downgrade() -> None:
    """Откат: удаляем новые индексы, возвращаем старый."""

    op.drop_index("idx_user_cards_last_date", table_name="user_cards")
    op.drop_index("idx_user_card_history_covering", table_name="user_card_history")

    op.create_index(
        "idx_user_card_history_user_id", "user_card_history", ["user_id", sa.text("opened_at DESC")]
    )
