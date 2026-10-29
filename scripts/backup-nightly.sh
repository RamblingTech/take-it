#!/bin/sh
# backup-nightly.sh runs forever in the "backup" container.
# Once a day, at BACKUP_TIME (02:00 unless .env says otherwise), it runs backup.sh.

BACKUP_TIME="${BACKUP_TIME:-02:00}"
echo "Nightly backups are on. They run every day at $BACKUP_TIME."

while true; do
  # Work out how many seconds until the next BACKUP_TIME...
  NOW=$(date +%s)
  NEXT=$(date -d "$BACKUP_TIME" +%s)
  # ...and if that time already passed today, aim for tomorrow instead.
  if [ "$NEXT" -le "$NOW" ]; then
    NEXT=$((NEXT + 86400))
  fi

  # Sleep until then, then make the backup. If it fails, say so and keep going.
  sleep $((NEXT - NOW))
  sh /scripts/backup.sh || echo "WARNING: tonight's backup failed."
done
