from __future__ import absolute_import

import pytz

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.db.migrations.writer import MigrationWriter
from django.test import TestCase
from django.utils import six

from timezone_field import TimeZoneField, TimeZoneFormField
from timezone_field.tests.models import FakeModel


PST = 'America/Los_Angeles'  # pytz.tzinfo.DstTzInfo
GMT = 'GMT'                  # pytz.tzinfo.StaticTzInfo
UTC = 'UTC'                  # pytz.UTC singleton

PST_tz = pytz.timezone(PST)
GMT_tz = pytz.timezone(GMT)
UTC_tz = pytz.timezone(UTC)

INVALID_TZ = 'ogga booga'
UNCOMMON_TZ = 'Singapore'

USA_TZS = [
    'US/Alaska',
    'US/Arizona',
    'US/Central',
    'US/Eastern',
    'US/Hawaii',
    'US/Mountain',
    'US/Pacific',
]


class TestForm(forms.Form):
    tz = TimeZoneFormField()
    tz_opt = TimeZoneFormField(required=False)


class FakeModelForm(forms.ModelForm):
    class Meta:
        model = FakeModel
        fields = '__all__'


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

    def test_invalid_uncommon_tz(self):
        form = TestForm({'tz': UNCOMMON_TZ})
        self.assertFalse(form.is_valid())


class TimeZoneFieldModelFormTestCase(TestCase):

    def test_valid_with_defaults(self):
        # seems there should be a better way to get a form's default values...?
        # http://stackoverflow.com/questions/7399490/
        data = dict(
            (field_name, field.initial)
            for field_name, field in six.iteritems(FakeModelForm().fields)
        )
        data.update({'tz': GMT})
        form = FakeModelForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(FakeModel.objects.count(), 1)

        m = FakeModel.objects.get()
        self.assertEqual(m.tz, GMT_tz)
        self.assertEqual(m.tz_opt, None)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_specify_all(self):
        form = FakeModelForm({
            'tz': UTC,
            'tz_opt': PST,
            'tz_opt_default': GMT,
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(FakeModel.objects.count(), 1)

        m = FakeModel.objects.get()
        self.assertEqual(m.tz, UTC_tz)
        self.assertEqual(m.tz_opt, PST_tz)
        self.assertEqual(m.tz_opt_default, GMT_tz)

    def test_invalid_not_blank(self):
        form = FakeModelForm({})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('required' in e for e in form.errors['tz']))

    def test_invalid_choice(self):
        form = FakeModelForm({'tz': INVALID_TZ})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('choice' in e for e in form.errors['tz']))

    def test_invalid_uncommmon_tz(self):
        form = FakeModelForm({'tz': UNCOMMON_TZ})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('choice' in e for e in form.errors['tz']))


class TimeZoneFieldTestCase(TestCase):

    def test_valid_dst_tz_objects(self):
        m = FakeModel.objects.create(tz=PST_tz, tz_opt=PST_tz,
                                     tz_opt_default=PST_tz)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, PST_tz)
        self.assertEqual(m.tz_opt, PST_tz)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_dst_tz_strings(self):
        m = FakeModel.objects.create(tz=PST, tz_opt=PST, tz_opt_default=PST)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, PST_tz)
        self.assertEqual(m.tz_opt, PST_tz)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_static_tz_objects(self):
        m = FakeModel.objects.create(tz=GMT_tz, tz_opt=GMT_tz,
                                     tz_opt_default=GMT_tz)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, GMT_tz)
        self.assertEqual(m.tz_opt, GMT_tz)
        self.assertEqual(m.tz_opt_default, GMT_tz)

    def test_valid_static_tz_strings(self):
        m = FakeModel.objects.create(tz=GMT, tz_opt=GMT, tz_opt_default=GMT)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, GMT_tz)
        self.assertEqual(m.tz_opt, GMT_tz)
        self.assertEqual(m.tz_opt_default, GMT_tz)

    def test_valid_UTC_object(self):
        m = FakeModel.objects.create(tz=UTC_tz, tz_opt=UTC_tz,
                                     tz_opt_default=UTC_tz)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, UTC_tz)
        self.assertEqual(m.tz_opt, UTC_tz)
        self.assertEqual(m.tz_opt_default, UTC_tz)

    def test_valid_UTC_string(self):
        m = FakeModel.objects.create(tz=UTC, tz_opt=UTC, tz_opt_default=UTC)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz, UTC_tz)
        self.assertEqual(m.tz_opt, UTC_tz)
        self.assertEqual(m.tz_opt_default, UTC_tz)

    def test_valid_default_values(self):
        m = FakeModel.objects.create(tz=UTC_tz)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_opt, None)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_default_values_without_saving_to_db(self):
        m = FakeModel(tz=UTC_tz)
        m.full_clean()
        self.assertEqual(m.tz_opt, None)
        self.assertEqual(m.tz_opt_default, PST_tz)

    def test_valid_blank_str(self):
        m = FakeModel.objects.create(tz=PST, tz_opt='')
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_opt, None)

    def test_valid_blank_none(self):
        m = FakeModel.objects.create(tz=PST, tz_opt=None)
        m.full_clean()
        m = FakeModel.objects.get(pk=m.pk)
        self.assertEqual(m.tz_opt, None)

    def test_string_value_lookup(self):
        FakeModel.objects.create(tz=PST)
        qs = FakeModel.objects.filter(tz=PST)
        self.assertEqual(qs.count(), 1)

    def test_tz_value_lookup(self):
        FakeModel.objects.create(tz=PST)
        qs = FakeModel.objects.filter(tz=PST_tz)
        self.assertEqual(qs.count(), 1)

    def test_invalid_blank(self):
        m = FakeModel()
        self.assertRaises(ValidationError, m.full_clean)

    def test_invalid_blank_str(self):
        m = FakeModel(tz='')
        self.assertRaises(ValidationError, m.full_clean)

    def test_invalid_blank_none(self):
        m = FakeModel(tz=None)
        self.assertRaises(ValidationError, m.full_clean)

    def test_invalid_choice(self):
        with self.assertRaises(ValidationError):
            FakeModel(tz=INVALID_TZ)

        with self.assertRaises(ValidationError):
            FakeModel(tz=4)

        with self.assertRaises(ValidationError):
            FakeModel(tz=object())


class TimeZoneFieldLimitedChoicesTestCase(TestCase):

    invalid_superset_tz = 'not a tz'
    invalid_subset_tz = 'Europe/Brussels'

    class FakeModelChoice(models.Model):
        tz_superset = TimeZoneField(
            choices=[(tz, tz) for tz in pytz.all_timezones],
            blank=True,
        )
        tz_subset = TimeZoneField(
            choices=[(tz, tz) for tz in USA_TZS],
            blank=True,
        )

    class FakeModelOldChoiceFormat(models.Model):
        tz_superset = TimeZoneField(
            choices=[(pytz.timezone(tz), tz) for tz in pytz.all_timezones],
            blank=True,
        )
        tz_subset = TimeZoneField(
            choices=[(pytz.timezone(tz), tz) for tz in USA_TZS],
            blank=True,
        )

    def test_valid_choice(self):
        self.FakeModelChoice.objects.create(tz_superset=PST, tz_subset=PST)
        m = self.FakeModelChoice.objects.get()
        self.assertEqual(m.tz_superset, PST_tz)
        self.assertEqual(m.tz_subset, PST_tz)

    def test_invalid_choice(self):
        with self.assertRaises(ValidationError):
            self.FakeModelChoice(tz_superset=self.invalid_superset_tz)

        with self.assertRaises(ValidationError):
            m = self.FakeModelChoice(tz_subset=self.invalid_subset_tz)
            m.full_clean()

    def test_valid_choice_old_format(self):
        self.FakeModelOldChoiceFormat.objects.create(
            tz_superset=PST, tz_subset=PST,
        )
        m = self.FakeModelOldChoiceFormat.objects.get()
        self.assertEqual(m.tz_superset, PST_tz)
        self.assertEqual(m.tz_subset, PST_tz)

    def test_invalid_choice_old_format(self):
        with self.assertRaises(ValidationError):
            self.FakeModelOldChoiceFormat(tz_superset=self.invalid_superset_tz)

        with self.assertRaises(ValidationError):
            m = self.FakeModelOldChoiceFormat(tz_subset=self.invalid_subset_tz)
            m.full_clean()


class TimeZoneFieldDeconstructTestCase(TestCase):

    test_fields = (
        TimeZoneField(),
        TimeZoneField(max_length=42),
        TimeZoneField(choices=[
            (pytz.timezone('US/Pacific'), 'US/Pacific'),
            (pytz.timezone('US/Eastern'), 'US/Eastern'),
        ]),
        TimeZoneField(choices=[
            ('US/Pacific', 'US/Pacific'),
            ('US/Eastern', 'US/Eastern'),
        ]),
    )

    def test_deconstruct(self):
        for org_field in self.test_fields:
            name, path, args, kwargs = org_field.deconstruct()
            new_field = TimeZoneField(*args, **kwargs)
            self.assertEqual(org_field.max_length, new_field.max_length)
            self.assertEqual(org_field.choices, new_field.choices)

    def test_full_serialization(self):
        # ensure the values passed to kwarg arguments can be serialized
        # the recommended 'deconstruct' testing by django docs doesn't cut it
        # https://docs.djangoproject.com/en/1.7/howto/custom-model-fields/#field-deconstruction
        # replicates https://github.com/mfogel/django-timezone-field/issues/12
        for field in self.test_fields:
            # ensuring the following call doesn't throw an error
            MigrationWriter.serialize(field)

    def test_default_kwargs_not_frozen(self):
        """
        Ensure the deconstructed representation of the field does not contain
        kwargs if they match the default.
        Don't want to bloat everyone's migration files.
        """
        field = TimeZoneField()
        name, path, args, kwargs = field.deconstruct()
        self.assertNotIn('choices', kwargs)
        self.assertNotIn('max_length', kwargs)

    def test_specifying_defaults_not_frozen(self):
        """
        If someone's matched the default values with their kwarg args, we
        shouldn't bothering freezing those.
        """
        field = TimeZoneField(max_length=63)
        name, path, args, kwargs = field.deconstruct()
        self.assertNotIn('max_length', kwargs)

        choices = [(pytz.timezone(tz), tz) for tz in pytz.common_timezones]
        field = TimeZoneField(choices=choices)
        name, path, args, kwargs = field.deconstruct()
        self.assertNotIn('choices', kwargs)

        choices = [(tz, tz) for tz in pytz.common_timezones]
        field = TimeZoneField(choices=choices)
        name, path, args, kwargs = field.deconstruct()
        self.assertNotIn('choices', kwargs)
