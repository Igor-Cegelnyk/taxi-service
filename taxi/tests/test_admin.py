from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self) -> None:
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="admin12345"

        )
        self.client.force_login(self.admin_user)
        self.driver = get_user_model().objects.create_user(
            username="user",
            password="user12345",
            license_number="test license"
        )

    def test_driver_license_number_listed(self):
        """Tests that driver's license number is in list_display on driver admin page """
        url = reverse("admin:taxi_driver_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.driver.license_number)

    def test_driver_detailed_license_number_listed(self):
        """Tests that driver's license number is on driver detail admin page """
        url = reverse("admin:taxi_driver_change", args=[self.driver.id])
        response = self.client.get(url)

        self.assertContains(response, self.driver.license_number)

    def test_add_driver(self):
        """Tests that additional info is when add new driver"""
        url = reverse("admin:taxi_driver_add")
        response = self.client.get(url)

        self.assertContains(response, "first_name")
        self.assertContains(response, "last_name")
        self.assertContains(response, "license_number")
