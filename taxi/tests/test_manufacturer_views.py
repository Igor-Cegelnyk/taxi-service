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
        self.user = get_user_model().objects.create(
            username="test",
            password="test12345"
        )
        self.client.force_login(self.user)

        for manufacturer_num in range(1, 7):
            Manufacturer.objects.create(
                name='Test %s' % manufacturer_num,
                country='Test country %s' % manufacturer_num,
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

    def test_lists_all_authors(self):
        """The test checks the next page for correct display of pagination"""
        for num in range(2, 4):
            response = self.client.get(MANUFACTURER_URL + f"?page={num}")
            self.assertEqual(response.status_code, 200)
            self.assertTrue("is_paginated" in response.context)
            self.assertTrue(response.context["is_paginated"] is True)
            self.assertTrue(len(response.context["manufacturer_list"]) == 2)

    def test_manufacturer_create_views(self):
        response = self.client.get("/manufacturers/create")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "name")
        self.assertContains(response, "country")

    def test_manufacturer_update_views(self):
        for manufacturer in Manufacturer.objects.all():
            id_ = manufacturer.id
            response = self.client.get(f"/manufacturers/{id_}/update")

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "name")
            self.assertContains(response, "country")

    def test_manufacturer_delete_views(self):
        for manufacturer in Manufacturer.objects.all():
            id_ = manufacturer.id
            response = self.client.get(f"/manufacturers/{id_}/delete")

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response, "taxi/manufacturer_delete.html"
            )
