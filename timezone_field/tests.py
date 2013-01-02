import pytz

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from . import TimeZoneField, TimeZoneFormField


PST = 'America/Los_Angeles'  # pytz.tzinfo.DstTzInfo
GMT = 'Etc/GMT'              # pytz.tzinfo.StaticTzInfo
UTC = 'UTC'                  # pytz.UTC singleton

PST_tz = pytz.timezone(PST)
GMT_tz = pytz.timezone(GMT)
UTC_tz = pytz.timezone(UTC)

INVALID_TZ = 'ogga booga'


class TestModel(models.Model):
    tz = TimeZoneField()
    tz_opt = TimeZoneField(blank=True, null=True)
    tz_opt_default = TimeZoneField(blank=True, default=PST)


class TestForm(forms.Form):
    tz = TimeZoneFormField()
    tz_opt = TimeZoneFormField(required=False)


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class TimeZoneFormFieldTestCase(TestCase):

    def test_valid1(self):
        form = TestForm({'tz': PST})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['tz'], PST_tz)
        self.assertEqual(form.cleaned_data['tz_opt'], None)

    def test_valid2(self):
        form = TestForm({'tz': GMT, 'tz_opt': UTC})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['tz'], GMT_tz)
        self.assertEqual(form.cleaned_data['tz_opt'], UTC_tz)

    def test_invalid_invalid_str(self):
        form = TestForm({'tz': INVALID_TZ})
        self.assertFalse(form.is_valid())


class TimeZoneFieldModelFormTestCase(TestCase):

    def test_valid_with_defaults(self):
        # seems there should be a better way to get a form's default values...?
        # http://stackoverflow.com/questions/7399490/
        data = dict(
            (field_name, field.initial)
            for field_name, field in TestModelForm().fields.iteritems()
        )
        data.update({'tz': GMT})
        form = TestModelForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

        m = TestModel.objects.get()
        self.assertEqual(m.tz, GMT_tz)
        self.assertEqual(m.tz_opt, None)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_specify_all(self):
        form = TestModelForm({
            'tz': UTC,
            'tz_opt': PST,
            'tz_opt_default': GMT,
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

        m = TestModel.objects.get()
        self.assertEqual(m.tz, UTC_tz)
        self.assertEqual(m.tz_opt, PST_tz)
        self.assertEqual(m.tz_opt_default, GMT_tz)

    def test_invalid_not_blank(self):
        form = TestModelForm({})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('required' in e for e in form.errors['tz']))

    def test_invalid_choice(self):
        form = TestModelForm({'tz': INVALID_TZ})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('choice' in e for e in form.errors['tz']))


class TimeZoneFieldTestCase(TestCase):

    def test_valid_dst_tz_objects(self):
        m = TestModel.objects.create(tz=PST_tz, tz_opt=PST_tz,
                                     tz_opt_default=PST_tz)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, PST_tz)
        self.assertEqual(m.tz_opt, PST_tz)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_dst_tz_strings(self):
        m = TestModel.objects.create(tz=PST, tz_opt=PST, tz_opt_default=PST)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, PST_tz)
        self.assertEqual(m.tz_opt, PST_tz)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_static_tz_objects(self):
        m = TestModel.objects.create(tz=GMT_tz, tz_opt=GMT_tz,
                                     tz_opt_default=GMT_tz)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, GMT_tz)
        self.assertEqual(m.tz_opt, GMT_tz)
        self.assertEqual(m.tz_opt_default, GMT_tz)

    def test_valid_static_tz_strings(self):
        m = TestModel.objects.create(tz=GMT, tz_opt=GMT, tz_opt_default=GMT)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, GMT_tz)
        self.assertEqual(m.tz_opt, GMT_tz)
        self.assertEqual(m.tz_opt_default, GMT_tz)

    def test_valid_UTC_object(self):
        m = TestModel.objects.create(tz=UTC_tz, tz_opt=UTC_tz,
                                     tz_opt_default=UTC_tz)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, UTC_tz)
        self.assertEqual(m.tz_opt, UTC_tz)
        self.assertEqual(m.tz_opt_default, UTC_tz)

    def test_valid_UTC_string(self):
        m = TestModel.objects.create(tz=UTC, tz_opt=UTC, tz_opt_default=UTC)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, UTC_tz)
        self.assertEqual(m.tz_opt, UTC_tz)
        self.assertEqual(m.tz_opt_default, UTC_tz)

    def test_valid_default_values(self):
        m = TestModel.objects.create(tz=UTC_tz)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_opt, None)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_blank_str(self):
        m = TestModel.objects.create(tz=PST, tz_opt='')
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_opt, None)

    def test_valid_blank_none(self):
        m = TestModel.objects.create(tz=PST, tz_opt=None)
        m.full_clean()
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_opt, None)

    def test_string_value_lookup(self):
        TestModel.objects.create(tz=PST)
        qs = TestModel.objects.filter(tz=PST)
        self.assertEqual(qs.count(), 1)

    def test_tz_value_lookup(self):
        TestModel.objects.create(tz=PST)
        qs = TestModel.objects.filter(tz=PST_tz)
        self.assertEqual(qs.count(), 1)

    def test_invalid_blank(self):
        m = TestModel()
        self.assertRaises(ValidationError, m.full_clean)

    def test_invalid_blank_str(self):
        m = TestModel(tz='')
        self.assertRaises(ValidationError, m.full_clean)

    def test_invalid_blank_none(self):
        m = TestModel(tz=None)
        self.assertRaises(ValidationError, m.full_clean)

    def test_invalid_choice(self):
        with self.assertRaises(ValidationError):
            TestModel(tz=INVALID_TZ)
        with self.assertRaises(ValidationError):
            TestModel(tz=4)
        with self.assertRaises(ValidationError):
            TestModel(tz=object())


class TimeZoneFieldLimitedChoicesTestCase(TestCase):

    class TestModelChoice(models.Model):
        CHOICES = [(tz, tz) for tz in pytz.common_timezones]
        tz = TimeZoneField(choices=CHOICES)

    def test_valid_choice(self):
        m = self.TestModelChoice.objects.create(tz=PST)
        m = self.TestModelChoice.objects.get()
        self.assertEqual(m.tz, PST_tz)

    def test_invalid_choice(self):
        m1 = self.TestModelChoice(tz='Europe/Nicosia')
        self.assertRaises(ValidationError, m1.full_clean)
