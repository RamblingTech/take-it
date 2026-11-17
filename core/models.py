"""
models.py describes the "core" app's database tables.

A model is a Python class that Django turns into a database table.
Each field (name, logo, ...) becomes a column in that table.
"""

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


def validate_timezone(value):
    """Reject anything that isn't a real time zone name, like "America/Chicago"."""
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValidationError(f'"{value}" is not a known time zone. Try something like "America/Chicago".')


class Organization(models.Model):
    """
    The company running this copy of TAKE IT: its name, logo and time zone.

    There is only ever ONE Organization row (a "singleton"). If TAKE IT
    becomes a multi-company service later, each company gets its own row,
    and records point back to the one they belong to.
    """

    # The company name shown across the app.
    name = models.CharField(max_length=200, default="My Company")

    # An optional logo image. Uploaded files are saved in the media/logos folder.
    logo = models.ImageField(upload_to="logos/", blank=True)

    # The company's time zone, used when showing dates and times.
    default_timezone = models.CharField(
        max_length=64,
        default="UTC",
        validators=[validate_timezone],
        help_text="Used for showing dates and times, and for the nightly backup schedule.",
    )

    # ---- Nightly backups (read by the backup container every minute) ----

    # What time of day, in the time zone above, the nightly backup runs.
    backup_time = models.TimeField(
        default=datetime.time(2, 0),
        help_text="The time of day the nightly backup runs, e.g. 02:00.",
    )

    # How many days of backups to keep. Older backup files are deleted.
    backup_keep_days = models.PositiveIntegerField(
        default=14,
        validators=[MinValueValidator(1)],
        help_text="Backups older than this many days are deleted automatically.",
    )

    class Meta:
        # How the table is named on the admin pages.
        verbose_name = "organization settings"
        verbose_name_plural = "organization settings"

    def __str__(self):
        # What Django shows when it needs a one-line label for this record.
        return self.name

    def save(self, *args, **kwargs):
        # Always save as row number 1, so a second Organization can never appear.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Get the one Organization, creating it with defaults the first time."""
        organization, created = cls.objects.get_or_create(pk=1)
        return organization
