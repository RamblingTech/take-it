"""
models.py for the "inventory" app: the building blocks that describe
TAKE IT's hardware.

It holds the "lookup" tables (lists an Admin fills in once and
then picks from: manufacturers, categories, statuses, locations, people,
device models), the custom fields, the Device itself, and its history.
"""

from django.conf import settings
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


class CustomField(models.Model):
    """
    An extra field an Admin adds to every device, e.g. "PO Number" or
    "Ticket #". Each company can add its own without changing any code.

    The definitions live here; each device stores its own values in
    Device.custom_data.
    """

    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    YES_NO = "yes_no"
    CHOICE = "choice"
    TYPE_CHOICES = [
        (TEXT, "Text"),
        (NUMBER, "Number"),
        (DATE, "Date"),
        (YES_NO, "Yes / No"),
        (CHOICE, "Pick from a list"),
    ]

    # The label people see, e.g. "PO Number".
    name = models.CharField(max_length=100, unique=True)
    # A short computer-friendly name, e.g. "po_number". It's the label the value
    # is saved under, so it should not change once devices have values.
    key = models.SlugField(
        max_length=50, unique=True,
        help_text='Lowercase letters, numbers and underscores only, e.g. "po_number". Don\'t change it later.',
    )
    field_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TEXT)
    # Only for "Pick from a list": the options, separated by commas.
    choices = models.TextField(blank=True, help_text='For "Pick from a list" only: the options, separated by commas.')
    required = models.BooleanField(default=False)
    help_text = models.CharField(max_length=200, blank=True)
    # Lower numbers are shown first on the device form.
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def choice_list(self):
        """The list options as a Python list: "Red, Blue" -> ["Red", "Blue"]."""
        return [option.strip() for option in self.choices.split(",") if option.strip()]


class Device(models.Model):
    """One physical piece of hardware, tracked by its asset tag."""

    # The company's own label on the device. No two devices can share one.
    asset_tag = models.CharField(max_length=50, unique=True)
    # The manufacturer's serial number. Optional, but if filled in it must be unique (see Meta).
    serial = models.CharField(max_length=100, blank=True)
    # An optional friendly name, e.g. "Front desk PC".
    name = models.CharField(max_length=150, blank=True)

    model = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)

    # Who has it and where it is. These are tracked SEPARATELY on purpose:
    # a device can be with a person AND at a location at the same time.
    # related_name: lets us ask a person "which devices do you hold?" (person.devices_held).
    current_holder = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.PROTECT, related_name="devices_held",
    )
    current_location = models.ForeignKey(
        Location, null=True, blank=True, on_delete=models.PROTECT, related_name="devices_here",
    )

    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    # Values for the Admin's custom fields, saved as {"po_number": "12345", ...}.
    # JSONField stores a whole dictionary in one column, so new custom fields
    # never need a database change.
    custom_data = models.JSONField(default=dict, blank=True)

    # auto_now_add: filled in automatically when the device is first saved.
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now: updated automatically every time the device is saved.
    updated_at = models.DateTimeField(auto_now=True)
    # The TAKE IT user who added it. settings.AUTH_USER_MODEL is Django's User table.
    # SET_NULL: if that user account is deleted, keep the device and leave this blank.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )

    class Meta:
        ordering = ["asset_tag"]
        constraints = [
            # A serial number can't appear twice, but many devices may leave it blank.
            models.UniqueConstraint(
                fields=["serial"], condition=~models.Q(serial=""), name="unique_serial_when_filled_in",
            ),
        ]

    def __str__(self):
        return f"{self.asset_tag} ({self.name or self.model})"


class ActivityLog(models.Model):
    """
    The history book: one line for everything that happens to a device.
    Reports are built from this later, so entries are never edited.
    """

    CREATED = "created"
    UPDATED = "updated"
    CHECKOUT = "checkout"
    CHECKIN = "checkin"
    STATUS_CHANGE = "status_change"
    ACTION_CHOICES = [
        (CREATED, "Created"),
        (UPDATED, "Updated"),
        (CHECKOUT, "Checked out"),
        (CHECKIN, "Checked in"),
        (STATUS_CHANGE, "Status changed"),
    ]

    # CASCADE: if a device is ever deleted, its history goes with it.
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="activity")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    # Who and where the device went to, and its status, at the time of this entry.
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    status = models.ForeignKey(Status, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    notes = models.TextField(blank=True)
    # db_index: makes "show activity between these dates" fast for reports.
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    # The TAKE IT user who did it.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        # Newest first.
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.get_action_display()}: {self.device.asset_tag}"

    @classmethod
    def record(cls, device, action, user=None, notes=""):
        """
        Write one history line for a device, copying its current holder,
        location and status so the entry stays accurate even if they change later.
        """
        return cls.objects.create(
            device=device,
            action=action,
            person=device.current_holder,
            location=device.current_location,
            status=device.status,
            notes=notes,
            user=user,
        )
