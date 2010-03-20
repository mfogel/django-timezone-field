import re

from datetime import datetime

from django import forms
from django.conf import settings
from django.test import TestCase

import timezones.forms
import timezones.timezones_tests.models as test_models

from timezones.utils import localtime_for_timezone, adjust_datetime_to_timezone



class TimeZoneTestCase(TestCase):
    
    def setUp(self):
        # ensure UTC
        self.ORIGINAL_TIME_ZONE = settings.TIME_ZONE
        settings.TIME_ZONE = "UTC"
    
    def tearDown(self):
        settings.TIME_ZONE = self.ORIGINAL_TIME_ZONE


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


class LocalizedDateTimeFieldTestCase(TimeZoneTestCase):
    
    def test_forms_clean_required(self):
        # the default case where no timezone is given explicitly. uses settings.TIME_ZONE.
        f = timezones.forms.LocalizedDateTimeField()
        self.assertEqual(
            repr(f.clean("2008-05-30 14:30:00")),
            "datetime.datetime(2008, 5, 30, 14, 30, tzinfo=<UTC>)"
        )
        self.assertRaises(forms.ValidationError, f.clean, "")
    
    def test_forms_clean_required(self):
        # the default case where no timezone is given explicitly. uses settings.TIME_ZONE.
        f = timezones.forms.LocalizedDateTimeField(required=False)
        self.assertEqual(
            repr(f.clean("2008-05-30 14:30:00")),
            "datetime.datetime(2008, 5, 30, 14, 30, tzinfo=<UTC>)"
        )
        self.assertEqual(f.clean(""), None)


# @@@ old doctests that have not been finished (largely due to needing to
# better understand how these bits were created and use-cases)
NOT_USED = {"API_TESTS": r"""
>>> class Foo(object):
...     datetime = datetime(2008, 6, 20, 23, 58, 17)
...     @decorators.localdatetime('datetime')
...     def localdatetime(self):
...         return 'Australia/Lindeman'
...
>>> foo = Foo()
>>> foo.datetime
datetime.datetime(2008, 6, 20, 23, 58, 17)
>>> foo.localdatetime
datetime.datetime(2008, 6, 21, 9, 58, 17, tzinfo=<DstTzInfo 'Australia/Lindeman' EST+10:00:00 STD>)
>>> foo.localdatetime = datetime(2008, 6, 12, 23, 50, 0)
>>> foo.datetime
datetime.datetime(2008, 6, 12, 13, 50, tzinfo=<UTC>)
>>> foo.localdatetime
datetime.datetime(2008, 6, 12, 23, 50, tzinfo=<DstTzInfo 'Australia/Lindeman' EST+10:00:00 STD>)
"""}