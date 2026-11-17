"""
The inventory app's web addresses. config/urls.py plugs these in under /devices/.
"""

from django.urls import path

from . import views

urlpatterns = [
    # /devices/  -> the list of devices
    path("", views.device_list, name="device_list"),
    # /devices/7/  -> device number 7. <int:pk> grabs the number and hands it to the view.
    path("<int:pk>/", views.device_detail, name="device_detail"),
]
