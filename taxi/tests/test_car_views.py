from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Car, Manufacturer

CAR_URL = reverse("taxi:car-list")


class PublicCarTest(TestCase):
    def test_login_required(self):
        response = self.client.get(CAR_URL)

        self.assertNotEqual(response.status_code, 200)


class PrivateCarTest(TestCase):
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

    def test_car_list_page_has_search(self):
        response = self.client.get(CAR_URL)

        self.assertTrue("search_form" in response.context)

    def test_car_pagination(self):
        """The test checks the next
        page for correct display of pagination"""
        for num in range(2, 4):
            response = self.client.get(CAR_URL, kwargs={"pk": num})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["is_paginated"] is True)

    def test_retrieve_car_detail_views(self):
        response = self.client.get(
            reverse("taxi:car-detail", kwargs={"pk": 2})
        )

        self.assertEqual(response.status_code, 200)

    def test_car_create_views(self):
        manufacturer = Manufacturer.objects.get(id=1)
        form_data = {
            "model": "New car",
            "manufacturer": manufacturer,
        }
        self.client.post(reverse("taxi:car-create"), data=form_data)
        new_car = Car.objects.get(model=form_data["model"])

        self.assertEqual(new_car.model, form_data["model"])

    def test_car_update_views(self):
        manufacturer = Manufacturer.objects.get(id=2)
        form_data = {
            "model": "New car update",
            "manufacturer": manufacturer,
        }
        new_car = Car.objects.get(id=2)
        self.client.post(reverse(
            "taxi:car-update", kwargs={"pk": new_car.id}),
            deta=form_data
        )

        self.assertEqual(new_car.model, form_data["model"])

    def test_car_delete_views_request(self):
        response = self.client.get(
            reverse("taxi:car-delete", kwargs={"pk": 2})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "taxi/car_delete.html"
        )

    def test_post_car_delete_views_request(self):
        post_response = self.client.delete(
            reverse("taxi:manufacturer-delete", kwargs={"pk": 2})
        )
        self.assertRedirects(post_response, reverse("taxi:manufacturer-list"), status_code=302)

    def test_assign_driver_to_car(self):
        """The test checks whether there is information
        about the assign/delete user's car on the screen"""
        car = Car.objects.get(id=1)
        response = self.client.get(reverse("taxi:car-detail", kwargs={"pk": 1}))
        if self.user in car.drivers.all():
            self.assertContains(response, "Delete me for this car")
        else:
            self.assertContains(response, "Assign me to this car")

    def test_post_assign_delete_driver_to_car(self):
        car = Car.objects.get(id=3)
        drivers_car = car.drivers.all().prefetch_related("cars")
        if self.user in drivers_car:
            self.client.post(
                reverse("taxi:car-detail", kwargs={"pk": car.id}),
                car.drivers.remove(self.user)
            )
            drivers_car = car.drivers.all().prefetch_related("cars")
            self.assertFalse(self.user in drivers_car)
        else:
            self.client.post(
                reverse("taxi:car-detail", kwargs={"pk": car.id}),
                car.drivers.add(self.user)
            )
            drivers_car = car.drivers.all().prefetch_related("cars")
            self.assertTrue(self.user in drivers_car)
