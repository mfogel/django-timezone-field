import pytz

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from timezone_field.fields import TimeZoneField


PST = 'America/Los_Angeles'
EST = 'America/New_York'
INVALID_TZ = 'ogga booga'


class TestModel(models.Model):
    tz_not_blank = TimeZoneField()
    tz_blank = TimeZoneField(blank=True)
    tz_blank_null = TimeZoneField(blank=True, null=True)


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class TimeZoneFieldModelFormTestCase(TestCase):

    def test_valid1(self):
        form = TestModelForm({'tz_not_blank': PST})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

    def test_valid2(self):
        form = TestModelForm({
            'tz_not_blank': PST,
            'tz_blank': EST,
            'tz_blank_null': EST,
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

    def test_invalid_not_blank(self):
        form = TestModelForm()
        self.assertFalse(form.is_valid())

    def test_invalid_invalid_str(self):
        form = TestModelForm({'tz_not_blank': INVALID_TZ})
        self.assertFalse(form.is_valid())


class TimeZoneFieldDBTestCase(TestCase):

    def test_valid_strings(self):
        m = TestModel.objects.create(
            tz_not_blank=PST,
            tz_blank=EST,
            tz_blank_null=EST,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_not_blank, pytz.timezone(PST))
        self.assertEqual(m.tz_blank, pytz.timezone(EST))
        self.assertEqual(m.tz_blank_null, pytz.timezone(EST))

    def test_valid_tzinfos(self):
        m = TestModel.objects.create(
            tz_not_blank=pytz.timezone(PST),
            tz_blank=pytz.timezone(PST),
            tz_blank_null=pytz.timezone(EST),
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_not_blank, pytz.timezone(PST))
        self.assertEqual(m.tz_blank, pytz.timezone(PST))
        self.assertEqual(m.tz_blank_null, pytz.timezone(EST))

    def test_valid_blank_str(self):
        m = TestModel.objects.create(
            tz_not_blank=PST,
            tz_blank='',
            tz_blank_null='',
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_not_blank, pytz.timezone(PST))
        self.assertIsNone(m.tz_blank)
        self.assertIsNone(m.tz_blank_null)

    def test_valid_blank_none(self):
        m = TestModel.objects.create(
            tz_not_blank=PST,
            tz_blank=None,
            tz_blank_null=None,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_not_blank, pytz.timezone(PST))
        self.assertIsNone(m.tz_blank)
        self.assertIsNone(m.tz_blank_null)

    def test_string_value_lookup(self):
        TestModel.objects.create(tz_not_blank=EST)
        qs = TestModel.objects.filter(tz_not_blank=EST)
        self.assertEqual(qs.count(), 1)

    def test_tz_value_lookup(self):
        TestModel.objects.create(tz_not_blank=EST)
        qs = TestModel.objects.filter(tz_not_blank=pytz.timezone(EST))
        self.assertEqual(qs.count(), 1)

    def test_invalid_blank_str(self):
        m = TestModel(tz_not_blank='')
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_invalid_blank_none(self):
        m = TestModel(tz_not_blank=None)
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_invalid_string(self):
        with self.assertRaises(ValidationError):
            TestModel(tz_not_blank=INVALID_TZ)
