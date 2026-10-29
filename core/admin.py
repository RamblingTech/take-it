"""
admin.py puts the core app's tables on Django's admin pages (/admin).
"""

from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin page for the Organization settings."""

    def has_add_permission(self, request):
        # Hide the "Add" button once the one Organization exists.
        return not Organization.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # The Organization can be edited but never deleted.
        return False
