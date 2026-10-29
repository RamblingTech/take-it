"""
urls.py is TAKE IT's map of web addresses.

Each path() line says: "when someone visits this address, show this page".
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # http://localhost:8000/admin/ shows Django's built-in admin pages.
    path("admin/", admin.site.urls),
]

# While building (DEBUG on), let Django itself serve uploaded files like the logo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
