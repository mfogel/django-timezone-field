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
    tz = TimeZoneField()
    tz_null = TimeZoneField(null=True)
    tz_blank = TimeZoneField(blank=True)
    tz_blank_null = TimeZoneField(blank=True, null=True)


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class TimeZoneFieldModelFormTestCase(TestCase):

    def test_valid1(self):
        form = TestModelForm({'tz': PST, 'tz_null': EST})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

    def test_valid2(self):
        form = TestModelForm({
            'tz': PST,
            'tz_null': PST,
            'tz_blank': EST,
            'tz_blank_null': EST,
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

    def test_invalid_not_blank(self):
        form1 = TestModelForm({'tz': EST})
        form2 = TestModelForm({'tz_null': EST})
        form3 = TestModelForm()
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())
        self.assertFalse(form3.is_valid())

    def test_invalid_invalid_str(self):
        form1 = TestModelForm({'tz': INVALID_TZ})
        form2 = TestModelForm({'tz_blank_null': INVALID_TZ})
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())

    def test_invalid_type(self):
        form1 = TestModelForm({'tz': 4})
        form2 = TestModelForm({'tz_blank_null': object()})
        self.assertFalse(form1.is_valid())
        self.assertFalse(form2.is_valid())


class TimeZoneFieldDBTestCase(TestCase):

    def test_valid_strings(self):
        m = TestModel.objects.create(
            tz=PST,
            tz_null=PST,
            tz_blank=EST,
            tz_blank_null=EST,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(PST))
        self.assertEqual(m.tz_null, pytz.timezone(PST))
        self.assertEqual(m.tz_blank, pytz.timezone(EST))
        self.assertEqual(m.tz_blank_null, pytz.timezone(EST))

    def test_valid_tzinfos(self):
        m = TestModel.objects.create(
            tz=pytz.timezone(PST),
            tz_null=pytz.timezone(EST),
            tz_blank=pytz.timezone(PST),
            tz_blank_null=pytz.timezone(EST),
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(PST))
        self.assertEqual(m.tz_null, pytz.timezone(EST))
        self.assertEqual(m.tz_blank, pytz.timezone(PST))
        self.assertEqual(m.tz_blank_null, pytz.timezone(EST))

    def test_valid_blank_str(self):
        m = TestModel.objects.create(
            tz=PST,
            tz_null=EST,
            tz_blank='',
            tz_blank_null='',
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(PST))
        self.assertEqual(m.tz_null, pytz.timezone(EST))
        self.assertIsNone(m.tz_blank)
        self.assertIsNone(m.tz_blank_null)

    def test_valid_blank_none(self):
        m = TestModel.objects.create(
            tz=PST,
            tz_blank=None,
            tz_blank_null=None,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(PST))
        self.assertIsNone(m.tz_blank)
        self.assertIsNone(m.tz_blank_null)

    def test_string_value_lookup(self):
        TestModel.objects.create(tz=EST)
        qs = TestModel.objects.filter(tz=EST)
        self.assertEqual(qs.count(), 1)

    def test_tz_value_lookup(self):
        TestModel.objects.create(tz=EST)
        qs = TestModel.objects.filter(tz=pytz.timezone(EST))
        self.assertEqual(qs.count(), 1)

    def test_invalid_blank_str(self):
        m1 = TestModel(tz='')
        m2 = TestModel(tz_null='')
        self.assertRaises(ValidationError, m1.full_clean)
        self.assertRaises(ValidationError, m2.full_clean)

    def test_invalid_blank_none(self):
        m1 = TestModel(tz=None)
        m2 = TestModel(tz_null=None)
        self.assertRaises(ValidationError, m1.full_clean)
        self.assertRaises(ValidationError, m2.full_clean)

    def test_invalid_type(self):
        m1 = TestModel(tz=4)
        m2 = TestModel(tz_null=object())
        self.assertRaises(ValidationError, m1.full_clean)
        self.assertRaises(ValidationError, m2.full_clean)

    def test_invalid_string(self):
        with self.assertRaises(ValidationError):
            TestModel(tz=INVALID_TZ)
        with self.assertRaises(ValidationError):
            TestModel(tz_null=INVALID_TZ)
        with self.assertRaises(ValidationError):
            TestModel(tz_blank=INVALID_TZ)
        with self.assertRaises(ValidationError):
            TestModel(tz_blank_null=INVALID_TZ)
