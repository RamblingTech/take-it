#!/bin/sh
# backup-nightly.sh runs forever in the "backup" container.
#
# Once a minute it reads the backup time and time zone an Admin chose on
# the Organization settings page. When the clock in that time zone reaches
# the backup time, it runs backup.sh.

echo "Nightly backups are on. Schedule is set on the Organization settings page."

# Remembers the date of the last backup, so we only back up once per day.
LAST_RUN_DATE=""

while true; do
  # Ask the database for the settings. "|" separates the two values.
  # If the settings can't be read yet (e.g. first start), use safe defaults.
  SETTINGS=$(psql -tA -F "|" -c \
    "SELECT default_timezone, to_char(backup_time, 'HH24:MI') FROM core_organization WHERE id = 1" \
    2>/dev/null)
  ZONE=$(echo "$SETTINGS" | cut -d "|" -f 1)
  RUN_AT=$(echo "$SETTINGS" | cut -d "|" -f 2)
  ZONE=${ZONE:-UTC}
  RUN_AT=${RUN_AT:-02:00}

  # The current time and date in the company's time zone.
  NOW=$(TZ="$ZONE" date +%H:%M)
  TODAY=$(TZ="$ZONE" date +%Y-%m-%d)

  # Is it backup time, and have we not already backed up today?
  if [ "$NOW" = "$RUN_AT" ] && [ "$TODAY" != "$LAST_RUN_DATE" ]; then
    LAST_RUN_DATE="$TODAY"
    sh /scripts/backup.sh || echo "WARNING: tonight's backup failed."
  fi

  # Check again in a minute.
  sleep 60
done
