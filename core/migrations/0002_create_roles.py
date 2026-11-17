"""
A "data migration": instead of changing a table, it adds starting data.

This one creates the four role groups, so every new TAKE IT install
has them from day one.
"""

from django.db import migrations

ROLE_NAMES = ["Admin", "Technician", "Finance", "Management"]


def create_roles(apps, schema_editor):
    # Inside migrations we ask for the Group model this way, not with an import.
    Group = apps.get_model("auth", "Group")
    for name in ROLE_NAMES:
        # get_or_create: make the group only if it doesn't already exist.
        Group.objects.get_or_create(name=name)


def remove_roles(apps, schema_editor):
    # Runs only if we ever "undo" this migration.
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=ROLE_NAMES).delete()


class Migration(migrations.Migration):

    # Run after the Organization migration, and after Django's own login tables exist.
    dependencies = [
        ("core", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_roles, remove_roles),
    ]
