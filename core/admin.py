"""
admin.py puts the core app's tables on Django's admin pages (/admin).
"""

from zoneinfo import available_timezones

from django import forms
from django.contrib import admin

from .models import Organization


class OrganizationForm(forms.ModelForm):
    """The form on the Organization settings page."""

    # Show the time zone as a drop-down list of every real time zone,
    # instead of a blank box someone has to type into.
    default_timezone = forms.ChoiceField(
        label="Time zone",
        choices=[(zone, zone) for zone in sorted(available_timezones())],
        help_text=Organization._meta.get_field("default_timezone").help_text,
    )

    class Meta:
        model = Organization
        fields = "__all__"
        # Show the backup time as a simple time box, e.g. 02:00.
        widgets = {"backup_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M")}


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin page for the Organization settings."""

    form = OrganizationForm

    # Split the page into labelled sections.
    fieldsets = [
        ("Company", {"fields": ["name", "logo", "default_timezone"]}),
        ("Nightly backups", {"fields": ["backup_time", "backup_keep_days"]}),
    ]

    def has_add_permission(self, request):
        # Hide the "Add" button once the one Organization exists.
        return not Organization.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # The Organization can be edited but never deleted.
        return False
