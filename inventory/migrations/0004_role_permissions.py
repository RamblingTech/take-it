"""
A data migration: decides what each role is allowed to do with inventory.

Django automatically makes four permissions for every table:
"add", "change", "delete" and "view". Here we hand them out to the roles.
"""

from django.contrib.auth.management import create_permissions
from django.db import migrations

# Tables Technicians can add to and edit (but never delete from).
TECHNICIAN_CAN_EDIT = ["device", "person", "location", "manufacturer", "assetmodel"]

# Every inventory table (everyone with a role can at least view these).
ALL_TABLES = [
    "manufacturer", "category", "status", "location", "person",
    "assetmodel", "customfield", "device", "activitylog",
]


def give_permissions(apps, schema_editor):
    # Django normally creates permissions AFTER all migrations finish.
    # We need them now, so we ask Django to create them right away.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    inventory = Permission.objects.filter(content_type__app_label="inventory")

    # Admin: everything, in every part of TAKE IT (including users and settings).
    Group.objects.get(name="Admin").permissions.set(Permission.objects.all())

    # Technician: view everything; add and change some things; delete nothing.
    technician_codenames = [f"view_{table}" for table in ALL_TABLES]
    for table in TECHNICIAN_CAN_EDIT:
        technician_codenames += [f"add_{table}", f"change_{table}"]
    Group.objects.get(name="Technician").permissions.set(inventory.filter(codename__in=technician_codenames))

    # Finance and Management: look, don't touch.
    view_only = inventory.filter(codename__in=[f"view_{table}" for table in ALL_TABLES])
    Group.objects.get(name="Finance").permissions.set(view_only)
    Group.objects.get(name="Management").permissions.set(view_only)


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_device_customfield_activitylog"),
        ("core", "0002_create_roles"),
    ]

    # noop: undoing this migration simply leaves the permissions as they are.
    operations = [migrations.RunPython(give_permissions, migrations.RunPython.noop)]
