from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Manufacturer, Car, Driver

INDEX_URL = reverse("taxi:index")


class PublicIndexTest(TestCase):
    def test_home_page_required(self):
        response = self.client.get(INDEX_URL)

        self.assertNotEqual(response.status_code, 200)


class PrivateIndexTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test12345"
        )
        self.client.force_login(self.user)

        manufacturer = Manufacturer.objects.create(
            name="Test manufacturer",
            country="Test country"
        )

        Car.objects.create(
            model="Test model",
            manufacturer=manufacturer
        )

    def test_retrieve_home_page(self):
        response = self.client.get(INDEX_URL)

        self.assertEqual(response.status_code, 200)

    def test_home_page_context(self):
        num_drivers = Driver.objects.count()
        num_cars = Car.objects.count()
        num_manufacturers = Manufacturer.objects.count()

        form_data = {
            "num_drivers": num_drivers,
            "num_cars": num_cars,
            "num_manufacturers": num_manufacturers,
            "num_visits": 1
        }
        response = self.client.get(INDEX_URL)

        self.assertEqual(response.context["num_drivers"], form_data["num_drivers"])
        self.assertEqual(response.context["num_cars"], form_data["num_cars"])
        self.assertEqual(response.context["num_manufacturers"], form_data["num_manufacturers"])
        self.assertEqual(response.context["num_visits"], form_data["num_visits"])
