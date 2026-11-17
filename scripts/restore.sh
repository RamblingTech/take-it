#!/bin/sh
# restore.sh puts the database back the way it was in one backup file.
# WARNING: everything entered since that backup is replaced.
# To run it (pick a file name from the backups folder):
#   docker compose stop web
#   docker compose exec backup sh /scripts/restore.sh takeit-2026-10-29_0200.sql.gz
#   docker compose start web

set -e

# $1 is the first thing typed after the script name: the backup file.
if [ -z "$1" ]; then
  echo "Please say which backup to restore. These are available:"
  ls -1 /backups
  exit 1
fi

FILE="/backups/$1"
if [ ! -f "$FILE" ]; then
  echo "No backup called $1 was found in the backups folder."
  exit 1
fi

echo "Restoring $FILE ..."
# Unzip the backup and feed its SQL instructions to the database.
# ON_ERROR_STOP: stop immediately if anything goes wrong.
gunzip -c "$FILE" | psql --quiet -v ON_ERROR_STOP=1 > /dev/null
echo "Restore finished."
