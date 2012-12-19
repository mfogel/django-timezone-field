import pytz

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from timezone_field.fields import TimeZoneField


PST = 'America/Los_Angeles' # instance of pytz.tzinfo.DstTzInfo
GMT = 'Etc/GMT'             # instance of pytz.tzinfo.StaticTzInfo
UTC = 'UTC'                 # pytz.UTC singleton

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
        form = TestModelForm({'tz': PST, 'tz_null': UTC})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

    def test_valid2(self):
        form = TestModelForm({
            'tz': PST,
            'tz_null': PST,
            'tz_blank': GMT,
            'tz_blank_null': UTC,
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

    def test_invalid_not_blank(self):
        form1 = TestModelForm({'tz': PST})
        form2 = TestModelForm({'tz_null': PST})
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

    def test_valid_dst_tz_objects(self):
        m = TestModel.objects.create(
            tz=pytz.timezone(PST),
            tz_null=pytz.timezone(PST),
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(PST))
        self.assertEqual(m.tz_null, pytz.timezone(PST))

    def test_valid_dst_tz_strings(self):
        m = TestModel.objects.create(
            tz=PST,
            tz_null=PST,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(PST))
        self.assertEqual(m.tz_null, pytz.timezone(PST))

    def test_valid_static_tz_objects(self):
        m = TestModel.objects.create(
            tz=pytz.timezone(GMT),
            tz_null=pytz.timezone(GMT),
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(GMT))
        self.assertEqual(m.tz_null, pytz.timezone(GMT))

    def test_valid_static_tz_strings(self):
        m = TestModel.objects.create(
            tz=GMT,
            tz_null=GMT,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(GMT))
        self.assertEqual(m.tz_null, pytz.timezone(GMT))

    def test_valid_UTC_object(self):
        m = TestModel.objects.create(
            tz=pytz.UTC,
            tz_null=pytz.UTC,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.UTC)
        self.assertEqual(m.tz_null, pytz.UTC)

    def test_valid_UTC_string(self):
        m = TestModel.objects.create(
            tz=UTC,
            tz_null=UTC,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.UTC)
        self.assertEqual(m.tz_null, pytz.UTC)

    def test_valid_blank_str(self):
        m = TestModel.objects.create(
            tz=PST,
            tz_null=PST,
            tz_blank='',
            tz_blank_null='',
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, pytz.timezone(PST))
        self.assertEqual(m.tz_null, pytz.timezone(PST))
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
        TestModel.objects.create(tz=PST)
        qs = TestModel.objects.filter(tz=PST)
        self.assertEqual(qs.count(), 1)

    def test_tz_value_lookup(self):
        TestModel.objects.create(tz=PST)
        qs = TestModel.objects.filter(tz=pytz.timezone(PST))
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
        with self.assertRaises(ValidationError):
            TestModel(tz=4)
        with self.assertRaises(ValidationError):
            TestModel(tz_null=object())

    def test_invalid_string(self):
        with self.assertRaises(ValidationError):
            TestModel(tz=INVALID_TZ)
        with self.assertRaises(ValidationError):
            TestModel(tz_null=INVALID_TZ)
        with self.assertRaises(ValidationError):
            TestModel(tz_blank=INVALID_TZ)
        with self.assertRaises(ValidationError):
            TestModel(tz_blank_null=INVALID_TZ)

    def test_invalid_choice(self):
        class TestModelChoice(models.Model):
            CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.common_timezones]
            tz = TimeZoneField(choices=CHOICES)
        m1 = TestModelChoice(tz='Europe/Nicosia')
        self.assertRaises(ValidationError, m1.full_clean)
