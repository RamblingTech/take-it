"""
Automatic checks for the device pages. Run with:  python manage.py test
"""

from django.contrib.auth.models import Group, User
from django.test import TestCase

from .models import ActivityLog, AssetModel, Category, CustomField, Device, Manufacturer, Person, Status


class DevicePageTests(TestCase):
    def setUp(self):
        # A Finance user (view-only) is enough to look at device pages.
        viewer = User.objects.create_user("viewer", password="x")
        viewer.groups.add(Group.objects.get(name="Finance"))
        self.client.force_login(viewer)

        dell = Manufacturer.objects.create(name="Dell")
        apple = Manufacturer.objects.create(name="Apple")
        laptop = Category.objects.get(name="Laptop")
        ready = Status.objects.get(name="Ready to Deploy")
        latitude = AssetModel.objects.create(name="Latitude 7450", manufacturer=dell, category=laptop)
        macbook = AssetModel.objects.create(name="MacBook Air", manufacturer=apple, category=laptop)

        self.dell_laptop = Device.objects.create(asset_tag="A-001", serial="DL1", model=latitude, status=ready)
        self.mac = Device.objects.create(
            asset_tag="A-002", serial="MB1", model=macbook, status=ready,
            current_holder=Person.objects.create(name="Pat Lee"),
            custom_data={"po_number": "PO-555"},
        )
        CustomField.objects.create(name="PO Number", key="po_number")
        ActivityLog.record(self.mac, ActivityLog.CHECKOUT, notes="Hello from the log")

    def test_people_without_a_role_cannot_see_devices(self):
        self.client.force_login(User.objects.create_user("nobody", password="x"))
        self.assertEqual(self.client.get("/devices/").status_code, 403)

    def test_list_shows_all_devices(self):
        response = self.client.get("/devices/")
        self.assertContains(response, "A-001")
        self.assertContains(response, "A-002")

    def test_search_by_manufacturer(self):
        response = self.client.get("/devices/?q=apple")
        self.assertContains(response, "A-002")
        self.assertNotContains(response, "A-001")

    def test_search_by_person(self):
        response = self.client.get("/devices/?q=pat")
        self.assertContains(response, "A-002")
        self.assertNotContains(response, "A-001")

    def test_live_search_sends_back_only_the_table(self):
        response = self.client.get("/devices/?q=dell", headers={"HX-Request": "true"})
        self.assertContains(response, "A-001")
        self.assertNotContains(response, "<html")

    def test_detail_page_shows_custom_fields_and_history(self):
        response = self.client.get(f"/devices/{self.mac.pk}/")
        self.assertContains(response, "PO Number")
        self.assertContains(response, "PO-555")
        self.assertContains(response, "Checked out")
        self.assertContains(response, "Hello from the log")

    def test_missing_device_is_page_not_found(self):
        self.assertEqual(self.client.get("/devices/99999/").status_code, 404)
