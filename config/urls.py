"""
urls.py is TAKE IT's map of web addresses.

Each path() line says: "when someone visits this address, show this page".
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    # http://localhost:8000/admin/ shows Django's built-in admin pages.
    path("admin/", admin.site.urls),
]
