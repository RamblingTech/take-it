"""
admin.py puts the inventory lookup tables on the admin pages,
so an Admin can add, edit and search them.
"""

from django.contrib import admin

from .models import AssetModel, Category, Location, Manufacturer, Person, Status


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
