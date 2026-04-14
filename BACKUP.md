# Backup & Restore

## Restore from latest
gunzip -c /root/backups/tarot_latest.sql.gz | docker exec -i tarot_magerie_bot-postgres-1 psql -U bot_user tarot_bot

## Restore from specific date
gunzip -c /root/backups/tarot_2026-04-14_03-00.sql.gz | docker exec -i tarot_magerie_bot-postgres-1 psql -U bot_user tarot_bot