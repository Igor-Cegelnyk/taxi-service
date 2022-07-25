from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Driver

DRIVER_URL = reverse("taxi:driver-list")


class PublicCarTest(TestCase):
    def test_login_required(self):
        response = self.client.get(DRIVER_URL)

        self.assertNotEqual(response.status_code, 200)


class PrivateCarTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test12345"
        )
        self.client.force_login(self.user)

        for driver_num in range(1, 7):
            Driver.objects.create(
                username=f"driver {driver_num}",
                password=f"test12345 {driver_num}",
                license_number=f"license {driver_num}",
            )

    def test_retrieve_driver(self):
        response = self.client.get(DRIVER_URL)
        driver_list = Driver.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["driver_list"]),
            list(driver_list[:2])
        )

    def test_driver_pagination(self):
        response = self.client.get(DRIVER_URL)

        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertTrue(len(response.context["driver_list"]) == 2)

    def test_lists_all_drivers(self):
        """The test checks the next
        page for correct display of pagination"""
        for num in range(2, 4):
            response = self.client.get(DRIVER_URL, kwargs={"pk": num})

            self.assertEqual(response.status_code, 200)
            self.assertTrue("is_paginated" in response.context)
            self.assertTrue(response.context["is_paginated"] is True)
            self.assertTrue(len(response.context["driver_list"]) == 2)

    def test_retrieve_driver_detail_views(self):
        response = self.client.get(
            reverse("taxi:driver-detail", kwargs={"pk": 2})
        )

        self.assertEqual(response.status_code, 200)

    def test_driver_create_views(self):
        form_data = {
            "username": "user_test",
            "password1": "user12345",
            "password2": "user12345",
            "first_name": "User first name",
            "last_name": "User last name",
            "license_number": "AAA12345"
        }

        self.client.post(reverse("taxi:driver-create"), data=form_data)
        new_driver = Driver.objects.get(username=form_data["username"])

        self.assertEqual(new_driver.first_name, form_data["first_name"])
        self.assertEqual(new_driver.last_name, form_data["last_name"])
        self.assertEqual(new_driver.license_number, form_data["license_number"])

    def test_driver_license_update_views(self):
        form_data = {"license_number": "BBB12345"}

        self.client.post(
            reverse("taxi:driver-license", kwargs={"pk": 1}),
            data=form_data
        )

        new_driver = Driver.objects.get(id=1)

        self.assertEqual(new_driver.license_number, form_data["license_number"])

    def test_driver_delete_views_request(self):
        response = self.client.get(
            reverse("taxi:driver-delete", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_delete.html")

    def test_post_driver_delete_views_request(self):
        post_response = self.client.delete(
            reverse("taxi:driver-delete", kwargs={"pk": 3}),
        )
        self.assertRedirects(post_response, reverse("taxi:driver-list"), status_code=302)
