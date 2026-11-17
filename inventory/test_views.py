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


class DeviceEditingTests(TestCase):
    def setUp(self):
        self.tech = User.objects.create_user("tech", password="x")
        self.tech.groups.add(Group.objects.get(name="Technician"))
        self.client.force_login(self.tech)

        dell = Manufacturer.objects.create(name="Dell")
        self.latitude = AssetModel.objects.create(
            name="Latitude 7450", manufacturer=dell, category=Category.objects.get(name="Laptop"),
        )
        self.ready = Status.objects.get(name="Ready to Deploy")
        self.repair = Status.objects.get(name="In Repair")
        CustomField.objects.create(name="PO Number", key="po_number")
        CustomField.objects.create(name="Warranty ends", key="warranty_ends", field_type=CustomField.DATE)
        CustomField.objects.create(name="Encrypted", key="encrypted", field_type=CustomField.YES_NO)

    def form_data(self, **changes):
        """A filled-in Add/Edit form, with any changes we want for a test."""
        data = {
            "asset_tag": "A-100", "serial": "SN100", "name": "", "model": self.latitude.pk,
            "status": self.ready.pk, "purchase_date": "", "notes": "",
            "cf_po_number": "PO-1", "cf_warranty_ends": "2028-01-31", "cf_encrypted": "on",
        }
        data.update(changes)
        return data

    def test_technician_can_add_a_device_with_custom_fields(self):
        response = self.client.post("/devices/add/", self.form_data())
        device = Device.objects.get(asset_tag="A-100")
        self.assertRedirects(response, f"/devices/{device.pk}/")
        self.assertEqual(device.created_by, self.tech)
        self.assertEqual(device.custom_data, {"po_number": "PO-1", "warranty_ends": "2028-01-31", "encrypted": True})
        self.assertTrue(device.activity.filter(action=ActivityLog.CREATED).exists())

    def test_duplicate_asset_tag_shows_an_error_instead_of_saving(self):
        self.client.post("/devices/add/", self.form_data())
        response = self.client.post("/devices/add/", self.form_data(serial="OTHER"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(Device.objects.count(), 1)

    def test_changing_status_is_logged(self):
        self.client.post("/devices/add/", self.form_data())
        device = Device.objects.get(asset_tag="A-100")
        self.client.post(f"/devices/{device.pk}/edit/", self.form_data(status=self.repair.pk))
        change = device.activity.get(action=ActivityLog.STATUS_CHANGE)
        self.assertEqual(change.notes, "Ready to Deploy → In Repair")

    def test_technician_cannot_delete(self):
        self.client.post("/devices/add/", self.form_data())
        device = Device.objects.get(asset_tag="A-100")
        self.assertEqual(self.client.post(f"/devices/{device.pk}/delete/").status_code, 403)
        self.assertTrue(Device.objects.filter(pk=device.pk).exists())

    def test_admin_can_delete(self):
        self.client.post("/devices/add/", self.form_data())
        device = Device.objects.get(asset_tag="A-100")
        admin_user = User.objects.create_user("adm", password="x")
        admin_user.groups.add(Group.objects.get(name="Admin"))
        self.client.force_login(admin_user)
        self.assertRedirects(self.client.post(f"/devices/{device.pk}/delete/"), "/devices/")
        self.assertFalse(Device.objects.filter(pk=device.pk).exists())

    def test_finance_cannot_add_devices(self):
        finance = User.objects.create_user("fin", password="x")
        finance.groups.add(Group.objects.get(name="Finance"))
        self.client.force_login(finance)
        self.assertEqual(self.client.get("/devices/add/").status_code, 403)
        self.assertNotContains(self.client.get("/devices/"), "Add device")
