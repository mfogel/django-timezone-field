import pytz
import re

from django import forms
from django.conf import settings
from django.db import models
from django.test import TestCase

from timezone_field.forms import TimeZoneField as TimeZoneFormField
from timezone_field.fields import TimeZoneField as TimeZoneModelField


class TestModel(models.Model):
    timezone = TimeZoneModelField()


class TimeZoneTestCase(TestCase):

    def setUp(self):
        # ensure UTC
        self.ORIGINAL_TIME_ZONE = settings.TIME_ZONE
        settings.TIME_ZONE = "UTC"

    def tearDown(self):
        settings.TIME_ZONE = self.ORIGINAL_TIME_ZONE

    # little helpers

    def assertFormIsValid(self, form):
        is_valid = form.is_valid()
        self.assert_(is_valid,
            "Form did not validate (errors=%r, form=%r)" % (form._errors, form)
        )


class TimeZoneFieldTestCase(TimeZoneTestCase):

    def test_forms_clean_required(self):
        f = TimeZoneFormField()
        self.assertEqual(
            repr(f.clean("US/Eastern")),
            "<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>"
        )
        self.assertRaises(forms.ValidationError, f.clean, "")

    def test_forms_clean_not_required(self):
        f = TimeZoneFormField(required=False)
        self.assertEqual(
            repr(f.clean("US/Eastern")),
            "<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>"
        )
        self.assertEqual(f.clean(""), "")

    def test_forms_clean_bad_value(self):
        f = TimeZoneFormField()
        try:
            f.clean("BAD VALUE")
        except forms.ValidationError, e:
            self.assertEqual(e.messages, ["Select a valid choice. BAD VALUE is not one of the available choices."])

    def test_models_as_a_form(self):
        class TestModelForm(forms.ModelForm):
            class Meta:
                model = TestModel
        form = TestModelForm()
        rendered = form.as_p()
        self.assert_(
            bool(re.search(r'<option value="[\w/]+">\([A-Z]+(?:\+|\-)\d{4}\)\s[\w/]+</option>', rendered)),
            "Did not find pattern in rendered form"
        )

    def test_models_modelform_validation(self):
        class TestModelForm(forms.ModelForm):
            class Meta:
                model = TestModel
        form = TestModelForm({"timezone": "America/Denver"})
        self.assertFormIsValid(form)

    def test_models_modelform_save(self):
        class TestModelForm(forms.ModelForm):
            class Meta:
                model = TestModel
        form = TestModelForm({"timezone": "America/Denver"})
        self.assertFormIsValid(form)
        form.save()

    def test_models_string_value(self):
        p = TestModel(timezone="America/Denver")
        p.save()
        p = TestModel.objects.get(pk=p.pk)
        self.assertEqual(p.timezone, pytz.timezone("America/Denver"))

    def test_models_string_value_lookup(self):
        TestModel(timezone="America/Denver").save()
        qs = TestModel.objects.filter(timezone="America/Denver")
        self.assertEqual(qs.count(), 1)

    def test_models_tz_value(self):
        tz = pytz.timezone("America/Denver")
        p = TestModel(timezone=tz)
        p.save()
        p = TestModel.objects.get(pk=p.pk)
        self.assertEqual(p.timezone, tz)

    def test_models_tz_value_lookup(self):
        TestModel(timezone="America/Denver").save()
        qs = TestModel.objects.filter(timezone=pytz.timezone("America/Denver"))
        self.assertEqual(qs.count(), 1)
