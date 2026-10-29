"""
The core app's own web addresses. config/urls.py plugs these in.
"""

from django.urls import path

from . import views

urlpatterns = [
    # The home page, at http://localhost:8000/
    path("", views.home, name="home"),
]
