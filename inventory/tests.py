"""
Automatic checks for the inventory app. Run with:  python manage.py test
"""

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from .models import AssetModel, Category, Location, Manufacturer, Status


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
