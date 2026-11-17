"""
models.py for the "inventory" app: the building blocks that describe
TAKE IT's hardware.

This file holds the "lookup" tables: lists an Admin fills in once and
then picks from (manufacturers, categories, statuses, locations, people,
and device models). The Device table itself comes in the next piece.
"""

from django.db import models


class Manufacturer(models.Model):
    """A company that makes hardware, e.g. Dell, Apple, Lenovo."""

    # unique=True: the same manufacturer can't be entered twice.
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        # Lists of manufacturers are sorted A to Z by name.
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    """A kind of hardware, e.g. Laptop, Monitor, Dock."""

    # The two kinds of category. Each pair is (value saved in the database, label people see).
    ASSET = "asset"
    ACCESSORY = "accessory"
    TYPE_CHOICES = [
        (ASSET, "Asset (tracked one by one, with an asset tag)"),
        (ACCESSORY, "Accessory (counted in bulk, like mice or cables)"),
    ]

    name = models.CharField(max_length=100, unique=True)
    # choices=: the admin page shows a drop-down instead of a free text box.
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=ASSET)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Status(models.Model):
    """
    Where a device is in its life, e.g. Ready to Deploy, Deployed, In Repair.

    Each status has a "behavior" that tells TAKE IT how to treat devices
    in that status (for example, only "deployable" devices can be checked out).
    """

    DEPLOYABLE = "deployable"
    PENDING = "pending"
    UNDEPLOYABLE = "undeployable"
    ARCHIVED = "archived"
    BEHAVIOR_CHOICES = [
        (DEPLOYABLE, "Deployable (can be checked out)"),
        (PENDING, "Pending (not ready yet, e.g. being set up)"),
        (UNDEPLOYABLE, "Undeployable (e.g. broken, in repair)"),
        (ARCHIVED, "Archived (gone for good, e.g. retired, lost)"),
    ]

    name = models.CharField(max_length=100, unique=True)
    behavior = models.CharField(max_length=20, choices=BEHAVIOR_CHOICES, default=DEPLOYABLE)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "statuses"

    def __str__(self):
        return self.name


class Location(models.Model):
    """A place a device can be: a building, a room, a closet, a branch office."""

    name = models.CharField(max_length=100, unique=True)
    # A short code people use, e.g. "HQ-2" for headquarters, second floor. Optional.
    code = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)

    # A location can sit inside another one (Room 204 is inside Building A).
    # ForeignKey = "points to a row in another table" (here, the same table).
    # null=True, blank=True: it's optional, a top-level location has no parent.
    # on_delete=models.PROTECT: Django refuses to delete a location that has
    # sub-locations, so nothing is left pointing at a missing row.
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
        help_text="Optional: the larger location this one is inside.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Person(models.Model):
    """
    Someone devices get assigned to. People do NOT log in to TAKE IT;
    they're just records (employees, contractors, students...).
    """

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    # Where this person usually works. Optional.
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "people"

    def __str__(self):
        return self.name


class AssetModel(models.Model):
    """
    A specific product, e.g. "Latitude 7450" made by Dell, in the Laptop category.

    It's called AssetModel in the code (not just "Model") so it doesn't get
    mixed up with Django's own word "model". On screen it's just "Model".
    """

    name = models.CharField(max_length=150)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    # Optional: how many months until this model is due to be replaced (end of life).
    eol_months = models.PositiveIntegerField(
        "end of life (months)", null=True, blank=True,
        help_text="Optional: months from purchase until replacement is due.",
    )
    # Optional: warn when fewer than this many are ready to deploy (used by alerts later).
    min_qty = models.PositiveIntegerField(
        "minimum quantity", null=True, blank=True,
        help_text="Optional: the fewest you want on the shelf before reordering.",
    )

    class Meta:
        ordering = ["manufacturer__name", "name"]
        verbose_name = "model"
        # The same manufacturer can't have two models with the same name.
        constraints = [
            models.UniqueConstraint(fields=["manufacturer", "name"], name="unique_model_per_manufacturer"),
        ]

    def __str__(self):
        return f"{self.manufacturer} {self.name}"
