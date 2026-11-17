"""
Automatic checks for the inventory app. Run with:  python manage.py test
"""

from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from .models import (
    ActivityLog, AssetModel, Category, CustomField, Device, Location, Manufacturer, Person, Status,
)


class StarterDataTests(TestCase):
    def test_starter_categories_exist(self):
        for name in ["Laptop", "Desktop", "Monitor", "Dock", "Tablet", "Phone"]:
            self.assertTrue(Category.objects.filter(name=name).exists())

    def test_starter_statuses_have_the_right_behavior(self):
        self.assertEqual(Status.objects.get(name="Ready to Deploy").behavior, Status.DEPLOYABLE)
        self.assertEqual(Status.objects.get(name="In Repair").behavior, Status.UNDEPLOYABLE)
        self.assertEqual(Status.objects.get(name="Retired").behavior, Status.ARCHIVED)


class AssetModelTests(TestCase):
    def setUp(self):
        # setUp runs before each test: make a manufacturer and grab a category.
        self.dell = Manufacturer.objects.create(name="Dell")
        self.laptop = Category.objects.get(name="Laptop")

    def test_model_shows_manufacturer_and_name(self):
        latitude = AssetModel.objects.create(name="Latitude 7450", manufacturer=self.dell, category=self.laptop)
        self.assertEqual(str(latitude), "Dell Latitude 7450")

    def test_same_manufacturer_cannot_have_two_models_with_the_same_name(self):
        AssetModel.objects.create(name="Latitude 7450", manufacturer=self.dell, category=self.laptop)
        with self.assertRaises(IntegrityError):
            AssetModel.objects.create(name="Latitude 7450", manufacturer=self.dell, category=self.laptop)


class LocationTests(TestCase):
    def test_cannot_delete_a_location_that_has_rooms_inside_it(self):
        building = Location.objects.create(name="Building A")
        Location.objects.create(name="Room 204", parent=building)
        with self.assertRaises(ProtectedError):
            building.delete()


class DeviceTests(TestCase):
    def setUp(self):
        dell = Manufacturer.objects.create(name="Dell")
        self.latitude = AssetModel.objects.create(
            name="Latitude 7450", manufacturer=dell, category=Category.objects.get(name="Laptop"),
        )
        self.ready = Status.objects.get(name="Ready to Deploy")

    def make_device(self, asset_tag, serial=""):
        return Device.objects.create(asset_tag=asset_tag, serial=serial, model=self.latitude, status=self.ready)

    def test_two_devices_cannot_share_an_asset_tag(self):
        self.make_device("A-001")
        with self.assertRaises(IntegrityError):
            self.make_device("A-001")

    def test_two_devices_cannot_share_a_serial(self):
        self.make_device("A-001", serial="SN123")
        with self.assertRaises(IntegrityError):
            self.make_device("A-002", serial="SN123")

    def test_many_devices_can_have_a_blank_serial(self):
        self.make_device("A-001")
        self.make_device("A-002")
        self.assertEqual(Device.objects.count(), 2)

    def test_device_can_have_a_holder_and_a_location_at_the_same_time(self):
        device = self.make_device("A-001")
        device.current_holder = Person.objects.create(name="Pat Lee")
        device.current_location = Location.objects.create(name="Branch Office")
        device.save()
        device.refresh_from_db()
        self.assertEqual(device.current_holder.name, "Pat Lee")
        self.assertEqual(device.current_location.name, "Branch Office")

    def test_custom_field_values_are_saved_with_the_device(self):
        device = self.make_device("A-001")
        device.custom_data = {"po_number": "PO-555"}
        device.save()
        device.refresh_from_db()
        self.assertEqual(device.custom_data["po_number"], "PO-555")

    def test_activity_log_copies_who_and_where(self):
        device = self.make_device("A-001")
        device.current_holder = Person.objects.create(name="Pat Lee")
        entry = ActivityLog.record(device, ActivityLog.CHECKOUT)
        # Later the device comes back, but the old entry still says Pat had it.
        device.current_holder = None
        device.save()
        entry.refresh_from_db()
        self.assertEqual(entry.person.name, "Pat Lee")


class CustomFieldTests(TestCase):
    def test_choice_list_splits_on_commas(self):
        field = CustomField(name="Color", key="color", field_type=CustomField.CHOICE, choices="Red, Blue ,, Green")
        self.assertEqual(field.choice_list(), ["Red", "Blue", "Green"])


class RolePermissionTests(TestCase):
    def test_technician_can_add_and_edit_devices_but_not_delete(self):
        tech = User.objects.create_user("tech", password="x")
        tech.groups.add(Group.objects.get(name="Technician"))
        self.assertTrue(tech.has_perm("inventory.add_device"))
        self.assertTrue(tech.has_perm("inventory.change_device"))
        self.assertFalse(tech.has_perm("inventory.delete_device"))
        self.assertFalse(tech.has_perm("inventory.change_status"))

    def test_finance_can_only_view(self):
        finance = User.objects.create_user("fin", password="x")
        finance.groups.add(Group.objects.get(name="Finance"))
        self.assertTrue(finance.has_perm("inventory.view_device"))
        self.assertFalse(finance.has_perm("inventory.change_device"))

    def test_admin_role_can_delete(self):
        admin_user = User.objects.create_user("adm", password="x")
        admin_user.groups.add(Group.objects.get(name="Admin"))
        self.assertTrue(admin_user.has_perm("inventory.delete_device"))
        self.assertTrue(admin_user.has_perm("core.change_organization"))
