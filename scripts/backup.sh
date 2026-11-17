#!/bin/sh
# backup.sh makes ONE backup of the TAKE IT database, right now.
# It runs inside the "backup" container. To run it by hand:
#   docker compose exec backup sh /scripts/backup.sh

# Stop at the first error, so a failed backup is never mistaken for a good one.
set -e

# Read the company's time zone and how many days of backups to keep,
# from the Organization settings page. Use safe defaults if they're not set yet.
SETTINGS=$(psql -tA -F "|" -c \
  "SELECT default_timezone, backup_keep_days FROM core_organization WHERE id = 1" \
  2>/dev/null || true)
ZONE=$(echo "$SETTINGS" | cut -d "|" -f 1)
KEEP=$(echo "$SETTINGS" | cut -d "|" -f 2)
ZONE=${ZONE:-UTC}
KEEP=${KEEP:-14}

# Build a file name with today's date and time in the company's time zone,
# e.g. takeit-2026-10-29_0200.sql.gz
FILE="/backups/takeit-$(TZ="$ZONE" date +%Y-%m-%d_%H%M).sql.gz"

# pg_dump writes out the whole database as SQL instructions.
# --clean --if-exists: the backup first removes old tables, so a restore starts fresh.
# gzip squeezes the file down to a fraction of its size.
pg_dump --clean --if-exists | gzip > "$FILE"

echo "Backup saved: $FILE"

# Delete backups older than KEEP days.
find /backups -name "takeit-*.sql.gz" -mtime +"$KEEP" -print -delete
