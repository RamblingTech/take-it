"""
admin.py puts the inventory tables on the admin pages,
so an Admin can add, edit and search them.
"""

from django.contrib import admin

from .models import (
    ActivityLog, AssetModel, Category, CustomField, Device, Location, Manufacturer, Person, Status,
)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ["name"]  # adds a search box


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "type"]  # columns shown in the list
    list_filter = ["type"]           # filter panel on the right
    search_fields = ["name"]


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ["name", "behavior"]
    list_filter = ["behavior"]
    search_fields = ["name"]


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "parent"]
    search_fields = ["name", "code"]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "location"]
    list_filter = ["location"]
    search_fields = ["name", "email"]


@admin.register(AssetModel)
class AssetModelAdmin(admin.ModelAdmin):
    list_display = ["name", "manufacturer", "category", "eol_months", "min_qty"]
    list_filter = ["category", "manufacturer"]
    search_fields = ["name", "manufacturer__name"]


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "field_type", "required", "order"]
    # Fill in the key automatically from the name as the Admin types.
    prepopulated_fields = {"key": ["name"]}


class ActivityLogInline(admin.TabularInline):
    """Shows a device's history underneath it on the device's admin page (read-only)."""

    model = ActivityLog
    extra = 0
    fields = ["timestamp", "action", "person", "location", "status", "user", "notes"]
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["asset_tag", "name", "model", "status", "current_holder", "current_location"]
    list_filter = ["status", "model__category", "current_location"]
    search_fields = ["asset_tag", "serial", "name", "current_holder__name"]
    readonly_fields = ["created_at", "updated_at", "created_by"]
    inlines = [ActivityLogInline]

    def save_model(self, request, obj, form, change):
        # When a device is added from the admin, remember who added it and log it.
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        ActivityLog.record(obj, ActivityLog.UPDATED if change else ActivityLog.CREATED, user=request.user)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """The full history list. It can be read and searched, never changed."""

    list_display = ["timestamp", "device", "action", "person", "location", "user"]
    list_filter = ["action"]
    search_fields = ["device__asset_tag", "person__name"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
