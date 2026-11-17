"""
The inventory app's web addresses. config/urls.py plugs these in under /devices/.
"""

from django.urls import path

from . import views

urlpatterns = [
    # /devices/  -> the list of devices
    path("", views.device_list, name="device_list"),
    # /devices/add/  -> the "Add device" page
    path("add/", views.device_create, name="device_create"),
    # /devices/7/  -> device number 7. <int:pk> grabs the number and hands it to the view.
    path("<int:pk>/", views.device_detail, name="device_detail"),
    # /devices/7/edit/ and /devices/7/delete/
    path("<int:pk>/edit/", views.device_edit, name="device_edit"),
    path("<int:pk>/delete/", views.device_delete, name="device_delete"),
]
