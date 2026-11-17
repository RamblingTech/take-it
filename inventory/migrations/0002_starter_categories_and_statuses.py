"""
A data migration: gives every new TAKE IT install some sensible starting
categories and statuses. An Admin can rename, change or add to them.
"""

from django.db import migrations

STARTER_CATEGORIES = ["Laptop", "Desktop", "Monitor", "Dock", "Tablet", "Phone"]

# (status name, behavior)
STARTER_STATUSES = [
    ("Ready to Deploy", "deployable"),
    ("Deployed", "deployable"),
    ("In Repair", "undeployable"),
    ("Retired", "archived"),
    ("Lost/Stolen", "archived"),
]


def add_starters(apps, schema_editor):
    Category = apps.get_model("inventory", "Category")
    Status = apps.get_model("inventory", "Status")
    for name in STARTER_CATEGORIES:
        # defaults= is only used when the row is being created.
        Category.objects.get_or_create(name=name, defaults={"type": "asset"})
    for name, behavior in STARTER_STATUSES:
        Status.objects.get_or_create(name=name, defaults={"behavior": behavior})


def remove_starters(apps, schema_editor):
    Category = apps.get_model("inventory", "Category")
    Status = apps.get_model("inventory", "Status")
    Category.objects.filter(name__in=STARTER_CATEGORIES).delete()
    Status.objects.filter(name__in=[name for name, behavior in STARTER_STATUSES]).delete()


class Migration(migrations.Migration):

    dependencies = [("inventory", "0001_initial")]

    operations = [migrations.RunPython(add_starters, remove_starters)]
