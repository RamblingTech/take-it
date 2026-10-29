"""
tests.py holds automatic checks. Run them with:  python manage.py test
Each test sets up a situation and confirms TAKE IT behaves as expected.
"""

from django.contrib.auth.models import Group, User
from django.test import TestCase

from .models import Organization
from .roles import ADMIN, ALL_ROLES, FINANCE, TECHNICIAN, user_has_role


class RoleTests(TestCase):
    def test_all_four_roles_exist(self):
        for name in ALL_ROLES:
            self.assertTrue(Group.objects.filter(name=name).exists())

    def test_user_has_only_the_role_they_were_given(self):
        tech = User.objects.create_user("tech", password="x")
        tech.groups.add(Group.objects.get(name=TECHNICIAN))
        self.assertTrue(user_has_role(tech, TECHNICIAN))
        self.assertTrue(user_has_role(tech, ADMIN, TECHNICIAN))
        self.assertFalse(user_has_role(tech, FINANCE))

    def test_superuser_counts_as_admin(self):
        boss = User.objects.create_superuser("boss", password="x")
        self.assertTrue(user_has_role(boss, ADMIN))


class OrganizationTests(TestCase):
    def test_there_is_only_ever_one_organization(self):
        Organization(name="First").save()
        Organization(name="Second").save()
        self.assertEqual(Organization.objects.count(), 1)
        self.assertEqual(Organization.load().name, "Second")
