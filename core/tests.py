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


class LoginAndHomePageTests(TestCase):
    def test_home_page_sends_visitors_to_login(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_login_page_shows_tagline(self):
        response = self.client.get("/accounts/login/")
        self.assertContains(response, "Track Assets, Know Everything")

    def test_logged_in_user_sees_their_role(self):
        finance = User.objects.create_user("fin", password="x")
        finance.groups.add(Group.objects.get(name=FINANCE))
        self.client.force_login(finance)
        response = self.client.get("/")
        self.assertContains(response, "Finance")
        self.assertNotContains(response, "Open admin settings")


class OrganizationSettingsPageTests(TestCase):
    def test_admin_can_set_time_zone_and_backup_schedule(self):
        boss = User.objects.create_superuser("boss", password="x")
        self.client.force_login(boss)
        Organization.load()
        response = self.client.post("/admin/core/organization/1/change/", {
            "name": "Acme",
            "default_timezone": "America/Chicago",
            "backup_time": "03:30",
            "backup_keep_days": "30",
        })
        self.assertEqual(response.status_code, 302)  # 302 = saved, sent back to the list
        organization = Organization.load()
        self.assertEqual(organization.default_timezone, "America/Chicago")
        self.assertEqual(organization.backup_time.strftime("%H:%M"), "03:30")
        self.assertEqual(organization.backup_keep_days, 30)

    def test_time_zone_must_be_from_the_list(self):
        boss = User.objects.create_superuser("boss", password="x")
        self.client.force_login(boss)
        Organization.load()
        response = self.client.post("/admin/core/organization/1/change/", {
            "name": "Acme",
            "default_timezone": "Mars/Base",
            "backup_time": "02:00",
            "backup_keep_days": "14",
        })
        self.assertEqual(response.status_code, 200)  # 200 = page shown again with an error
        self.assertEqual(Organization.load().default_timezone, "UTC")
