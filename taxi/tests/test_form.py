from django.contrib.auth import get_user_model
from django.test import TestCase
from django import forms

from taxi.form import DriverCreationForm, DriverLicenseUpdateForm, CarForm, CarSearchForm


class FormsTests(TestCase):
    def test_driver_creation_form_with_license_fist_last_name_is_valid(self):
        form_data = {
            "username": "user_test",
            "password1": "user12345",
            "password2": "user12345",
            "first_name": "User first name",
            "last_name": "User last name",
            "license_number": "AAA12345"
        }

        form = DriverCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_field_license_number_help_text(self):
        form = DriverCreationForm()
        self.assertEqual(
            form.fields["license_number"].help_text,
            "<li>License number must contain exactly 8 characters</li>"
            "<li>First 3 characters are uppercase letters</li>"
            "<li>Last 5 characters are digits</li>"
        )

    def test_field_license_number_required(self):
        form = DriverCreationForm()
        self.assertEqual(
            form.fields["license_number"].required, True
        )

    def test_field_license_number_max_length(self):
        form = DriverCreationForm()
        self.assertEqual(
            form.fields["license_number"].max_length, 8
        )

    def test_driver_license_update_form(self):
        form_data = {
            "license_number": "BBB12345"
        }
        form = DriverLicenseUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_car_form_drivers_field_queryset(self):
        form = CarForm()
        self.assertQuerysetEqual(
            form.fields["drivers"].queryset,
            get_user_model().objects.all()
        )

    def test_car_form_drivers_field_drivers_is_model_multiple_choice(self):
        form = CarForm()
        self.assertTrue(
            form.fields["drivers"],
            forms.ModelMultipleChoiceField
        )

    def test_car_form_drivers_field_drivers_required(self):
        form = CarForm()
        self.assertEqual(
            form.fields["drivers"].required, False
        )

    def test_car_form_drivers_field_drivers_widget(self):
        form = CarForm()
        self.assertTrue(
            form.fields["drivers"].widget,
            forms.CheckboxSelectMultiple
        )

    def test_car_search_form_field_model_type_char_field(self):
        form = CarSearchForm()
        self.assertTrue(
            form.fields["model"],
            forms.CharField
        )

    def test_car_search_form_field_model_max_length(self):
        form = CarSearchForm()
        self.assertEqual(
            form.fields["model"].max_length,
            200
        )

    def test_car_search_form_field_model_required(self):
        form = CarSearchForm()
        self.assertEqual(
            form.fields["model"].required,
            False
        )

    def test_car_search_form_field_model_label(self):
        form = CarSearchForm()
        self.assertEqual(
            form.fields["model"].label, ""
        )

    def test_car_search_form_field_model_widget(self):
        form = CarSearchForm()
        self.assertTrue(
            form.fields["model"].widget,
            forms.TextInput(
                attrs={"placeholder": "Search by model.."}
            )
        )
