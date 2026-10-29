#!/bin/sh
# backup.sh makes ONE backup of the TAKE IT database, right now.
# It runs inside the "backup" container. To run it by hand:
#   docker compose exec backup sh /scripts/backup.sh

# Stop at the first error, so a failed backup is never mistaken for a good one.
set -e

# Build a file name with today's date and time, e.g. takeit-2026-10-29_0200.sql.gz
FILE="/backups/takeit-$(date +%Y-%m-%d_%H%M).sql.gz"

# pg_dump writes out the whole database as SQL instructions.
# --clean --if-exists: the backup first removes old tables, so a restore starts fresh.
# gzip squeezes the file down to a fraction of its size.
pg_dump --clean --if-exists | gzip > "$FILE"

echo "Backup saved: $FILE"

# Delete backups older than BACKUP_KEEP_DAYS days (14 unless .env says otherwise).
find /backups -name "takeit-*.sql.gz" -mtime +"${BACKUP_KEEP_DAYS:-14}" -print -delete
