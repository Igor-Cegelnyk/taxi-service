from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Car, Manufacturer
from taxi.views import CarListView

CAR_URL = reverse("taxi:car-list")


class PublicCarTest(TestCase):
    def test_login_required(self):
        response = self.client.get(CAR_URL)

        self.assertNotEqual(response.status_code, 200)


class PrivateCarTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(
            username="test",
            password="test12345"
        )
        self.client.force_login(self.user)

        for manufacturer_num in range(1, 7):
            Manufacturer.objects.create(
                name=f"Test {manufacturer_num}",
                country=f"Test country {manufacturer_num}",
            )
        for car_num in range(1, 7):
            Car.objects.create(
                model=f"Model {car_num}",
                manufacturer=Manufacturer.objects.get(id=car_num),
            )

    def test_retrieve_car(self):
        response = self.client.get(CAR_URL)
        car_list = Car.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["car_list"]),
            list(car_list[:2])
        )

    def test_car_pagination_and_search(self):
        response = self.client.get(CAR_URL)

        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertTrue(len(response.context["car_list"]) == 2)
        self.assertTrue("search_form" in response.context)

    def test_lists_all_cars(self):
        """The test checks the next
        page for correct display of pagination"""
        for num in range(2, 4):
            response = self.client.get(CAR_URL + f"?page={num}")
            self.assertEqual(response.status_code, 200)
            self.assertTrue("is_paginated" in response.context)
            self.assertTrue(response.context["is_paginated"] is True)
            self.assertTrue(len(response.context["car_list"]) == 2)

    def test_retrieve_car_detail_views(self):
        for car in Car.objects.all():
            id_ = car.id
            response = self.client.get(f"/cars/{id_}/")

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response, "taxi/car_detail.html"
            )

    def test_car_create_views(self):
        response = self.client.get("/cars/create")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "model")
        self.assertContains(response, "manufacturer")
        self.assertContains(response, "drivers")

    def test_car_update_views(self):
        for car in Car.objects.all():
            id_ = car.id
            response = self.client.get(f"/cars/{id_}/update")

            self.assertContains(response, "model")
            self.assertContains(response, "manufacturer")
            self.assertContains(response, "drivers")

    def test_car_delete_views(self):
        for car in Car.objects.all():
            id_ = car.id
            response = self.client.get(f"/car/{id_}/delete")

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response, "taxi/car_delete.html"
            )