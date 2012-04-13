import re

from datetime import datetime

import pytz

from django import forms
from django.conf import settings
from django.db import models
from django.test import TestCase

import timezones.forms
import timezones.timezones_tests.models as test_models

from timezones.fields import TimeZoneField
from timezones.utils import localtime_for_timezone, adjust_datetime_to_timezone



class Profile(models.Model):
    name = models.CharField(max_length=100)
    timezone = TimeZoneField()



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


class UtilsTestCase(TimeZoneTestCase):

    def test_localtime_for_timezone(self):
        self.assertEqual(
            localtime_for_timezone(
                datetime(2008, 6, 25, 18, 0, 0), "America/Denver"
            ).strftime("%m/%d/%Y %H:%M:%S"),
            "06/25/2008 12:00:00"
        )

    def test_adjust_datetime_to_timezone(self):
        self.assertEqual(
            adjust_datetime_to_timezone(
                datetime(2008, 6, 25, 18, 0, 0), "UTC"
            ).strftime("%m/%d/%Y %H:%M:%S"),
            "06/25/2008 18:00:00"
        )


class TimeZoneFieldTestCase(TimeZoneTestCase):

    def test_forms_clean_required(self):
        f = timezones.forms.TimeZoneField()
        self.assertEqual(
            repr(f.clean("US/Eastern")),
            "<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>"
        )
        self.assertRaises(forms.ValidationError, f.clean, "")

    def test_forms_clean_not_required(self):
        f = timezones.forms.TimeZoneField(required=False)
        self.assertEqual(
            repr(f.clean("US/Eastern")),
            "<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>"
        )
        self.assertEqual(f.clean(""), "")

    def test_forms_clean_bad_value(self):
        f = timezones.forms.TimeZoneField()
        try:
            f.clean("BAD VALUE")
        except forms.ValidationError, e:
            self.assertEqual(e.messages, ["Select a valid choice. BAD VALUE is not one of the available choices."])

    def test_models_as_a_form(self):
        class ProfileForm(forms.ModelForm):
            class Meta:
                model = test_models.Profile
        form = ProfileForm()
        rendered = form.as_p()
        self.assert_(
            bool(re.search(r'<option value="[\w/]+">\([A-Z]+(?:\+|\-)\d{4}\)\s[\w/]+</option>', rendered)),
            "Did not find pattern in rendered form"
        )

    def test_models_modelform_validation(self):
        class ProfileForm(forms.ModelForm):
            class Meta:
                model = test_models.Profile
        form = ProfileForm({"name": "Brian Rosner", "timezone": "America/Denver"})
        self.assertFormIsValid(form)

    def test_models_modelform_save(self):
        class ProfileForm(forms.ModelForm):
            class Meta:
                model = test_models.Profile
        form = ProfileForm({"name": "Brian Rosner", "timezone": "America/Denver"})
        self.assertFormIsValid(form)
        p = form.save()

    def test_models_string_value(self):
        p = test_models.Profile(name="Brian Rosner", timezone="America/Denver")
        p.save()
        p = test_models.Profile.objects.get(pk=p.pk)
        self.assertEqual(p.timezone, pytz.timezone("America/Denver"))

    def test_models_string_value_lookup(self):
        test_models.Profile(name="Brian Rosner", timezone="America/Denver").save()
        qs = test_models.Profile.objects.filter(timezone="America/Denver")
        self.assertEqual(qs.count(), 1)

    def test_models_tz_value(self):
        tz = pytz.timezone("America/Denver")
        p = test_models.Profile(name="Brian Rosner", timezone=tz)
        p.save()
        p = test_models.Profile.objects.get(pk=p.pk)
        self.assertEqual(p.timezone, tz)

    def test_models_tz_value_lookup(self):
        test_models.Profile(name="Brian Rosner", timezone="America/Denver").save()
        qs = test_models.Profile.objects.filter(timezone=pytz.timezone("America/Denver"))
        self.assertEqual(qs.count(), 1)
