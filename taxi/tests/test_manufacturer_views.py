from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Manufacturer

MANUFACTURER_URL = reverse("taxi:manufacturer-list")


class PublicManufacturerTest(TestCase):
    def test_login_required(self):
        response = self.client.get(MANUFACTURER_URL)

        self.assertNotEqual(response.status_code, 200)


class PrivateManufacturerTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test12345"
        )
        self.client.force_login(self.user)

        for manufacturer_num in range(1, 7):
            Manufacturer.objects.create(
                name=f"Test {manufacturer_num}",
                country=f"Test country {manufacturer_num}",
            )

    def test_retrieve_manufacturer(self):
        response = self.client.get(MANUFACTURER_URL)
        manufacturer_list = Manufacturer.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(manufacturer_list[:2])
        )

    def test_manufacturer_correct_template(self):
        response = self.client.get(MANUFACTURER_URL)

        self.assertTemplateUsed(
            response, "taxi/manufacturer_list.html"
        )

    def test_manufacturer_pagination(self):
        response = self.client.get(MANUFACTURER_URL)

        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertTrue(len(response.context["manufacturer_list"]) == 2)

    def test_lists_all_manufacturers(self):

        """The test checks the next page
        for correct display of pagination"""

        for num in range(2, 4):
            response = self.client.get(MANUFACTURER_URL, kwargs={"pk": num})
            self.assertEqual(response.status_code, 200)
            self.assertTrue("is_paginated" in response.context)
            self.assertTrue(response.context["is_paginated"] is True)
            self.assertTrue(len(response.context["manufacturer_list"]) == 2)

    def test_manufacturer_create_views(self):
        form_data = {
            "name": "New manufacturer",
            "country": "Ukraine",
        }
        self.client.post(
            reverse("taxi:manufacturer-create"),
            data=form_data
        )
        new_manufacturer = Manufacturer.objects.get(
            name=form_data["name"]
        )

        self.assertEqual(new_manufacturer.name, form_data["name"])
        self.assertEqual(new_manufacturer.country, form_data["country"])

    def test_manufacturer_update_views(self):
        form_data = {
            "name": "Test manufacturer",
            "country": "Test country",
        }
        self.client.post(reverse(
            "taxi:manufacturer-update", kwargs={"pk": 2}),
            data=form_data
        )
        new_manufacturer = Manufacturer.objects.get(id=2)

        self.assertEqual(new_manufacturer.name, form_data["name"])
        self.assertEqual(new_manufacturer.country, form_data["country"])

    def test_manufacturer_delete_views_request(self):
        response = self.client.get(
            reverse("taxi:manufacturer-delete", kwargs={"pk": 1}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "taxi/manufacturer_delete.html"
        )

    def test_post_manufacturer_delete_views_request(self):
        post_response = self.client.delete(
            reverse("taxi:manufacturer-delete", kwargs={"pk": 2}),
            follow=True
        )
        self.assertRedirects(post_response, reverse("taxi:manufacturer-list"), status_code=302)
