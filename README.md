# TAKE IT

**T**rack **A**ssets, **K**now **E**verything: a self-hosted IT hardware
asset-management system.

TAKE IT runs in Docker, so it works the same on a Windows PC, a Linux VM,
or a Raspberry Pi.

---

## What's inside

| Container | What it does |
|-----------|--------------|
| `web`     | The TAKE IT website (Python + Django). |
| `db`      | The PostgreSQL database, where all records are kept. |
| `backup`  | Backs up the database every night into the `backups` folder. |

---

## First-time setup

You need **Git** and **Docker** installed. On Windows, install
**Docker Desktop** and use **PowerShell 7**.

**1. Download TAKE IT**
```
git clone https://github.com/RamblingTech/take-it.git && cd take-it
```

**2. Create your settings file from the template**
```
copy .env.example .env
```
(On Linux or a Raspberry Pi, use `cp .env.example .env` instead.)

**3. Edit `.env`** in any text editor. At minimum, change:
- `DJANGO_SECRET_KEY` to a long random string
- `POSTGRES_PASSWORD` to a strong password
- `DJANGO_ALLOWED_HOSTS` to include this computer's IP address or name
- `TZ` to your time zone (for example `America/Chicago`)

**4. Build and start TAKE IT**
```
docker compose up -d --build
```

**5. Create the database tables**
```
docker compose exec web python manage.py migrate
```

**6. Create your first admin login**
```
docker compose exec web python manage.py createsuperuser
```

**7. Open TAKE IT** at http://localhost:8000 (or `http://<this computer's IP>:8000`)
and log in.

**8. Set up your company** in **Open admin settings > Organization settings**:
your company name, logo and time zone.

---

## Everyday commands

Start TAKE IT
```
docker compose up -d
```

Stop TAKE IT (your data is kept)
```
docker compose down
```

Get the latest version and apply any database changes
```
git pull && docker compose up -d --build && docker compose exec web python manage.py migrate
```

Run the automatic tests
```
docker compose exec web python manage.py test
```

See what a container is printing (press Ctrl+C to stop watching)
```
docker compose logs -f web
```

---

## Users and roles

Each person who logs in has one role. Give a user a role in
**Admin > Users > (pick the user) > Groups**.

| Role | Can do |
|------|--------|
| **Admin** | Everything: data, imports, settings, users. |
| **Technician** | Add and edit devices, check them in and out. No deleting, no settings. |
| **Finance** | Read-only (reports come later). |
| **Management** | Read-only dashboard. |

The people devices are assigned to (end users) don't log in. They are
just records in TAKE IT.

---

## Backups

The `backup` container saves a copy of the database every night at
`BACKUP_TIME` (set in `.env`, 02:00 by default) into the `backups` folder.
Backups older than `BACKUP_KEEP_DAYS` days (14 by default) are deleted
automatically.

**Make a backup right now**
```
docker compose exec backup sh /scripts/backup.sh
```

**Restore a backup.** This replaces everything entered since that
backup. Stop the website first:
```
docker compose stop web
```
Restore (swap in the file name you want from the `backups` folder; run
the command without a name to list them):
```
docker compose exec backup sh /scripts/restore.sh takeit-2026-10-29_0200.sql.gz
```
Start the website again:
```
docker compose start web
```

Tip: copy the `backups` folder to another machine or a network share now
and then. A backup on the same disk won't help if that disk dies.

---

## Where things live

| Path | What it is |
|------|------------|
| `.env` | Your private settings and passwords. Never shared or uploaded. |
| `config/` | The Django project: settings and the web address map. |
| `core/` | Organization settings, roles, login and the home page. |
| `templates/` | Page layouts shared across the whole site. |
| `scripts/` | Backup and restore scripts. |
| `backups/` | Database backups (not uploaded to Git). |
