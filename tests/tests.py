from __future__ import absolute_import

import pytz

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.db.migrations.writer import MigrationWriter
from django.test import TestCase
from rest_framework import serializers

from timezone_field import (
    TimeZoneField, TimeZoneFormField, TimeZoneSerializerField,
)
from timezone_field.utils import add_gmt_offset_to_choices
from tests.models import TestModel


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


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
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

    def test_invalid_choice(self):
        form = TestForm({'tz_invalid_choice': INVALID_TZ})
        self.assertFalse(form.is_valid())

    def test_invalid_uncommon_tz(self):
        form = TestForm({'tz': UNCOMMON_TZ})
        self.assertFalse(form.is_valid())

    def test_default_human_readable_choices_dont_have_underscores(self):
        form = TestForm()
        pst_choice = [c for c in form.fields['tz'].choices if c[0] == PST]
        self.assertEqual(pst_choice[0][1], 'America/Los Angeles')


class TestFormInvalidChoice(forms.Form):
    tz = TimeZoneFormField(
        choices=(
            [(tz, tz) for tz in pytz.all_timezones]
            + [(INVALID_TZ, pytz.UTC)]
        )
    )


class TimeZoneFormFieldInvalidChoideTestCase(TestCase):

    def test_valid(self):
        form = TestFormInvalidChoice({'tz': PST})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['tz'], PST_tz)

    def test_invalid_choide(self):
        form = TestFormInvalidChoice({'tz': INVALID_TZ})
        self.assertFalse(form.is_valid())


class TimeZoneFieldModelFormTestCase(TestCase):

    def test_valid_with_defaults(self):
        # seems there should be a better way to get a form's default values...?
        # http://stackoverflow.com/questions/7399490/
        data = dict(
            (field_name, field.initial)
            for field_name, field in TestModelForm().fields.items()
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
        self.assertEqual(m.tz_gmt_offset, None)

    def test_valid_specify_all(self):
        form = TestModelForm({
            'tz': UTC,
            'tz_opt': PST,
            'tz_opt_default': GMT,
            'tz_gmt_offset': UTC,
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

        m = TestModel.objects.get()
        self.assertEqual(m.tz, UTC_tz)
        self.assertEqual(m.tz_opt, PST_tz)
        self.assertEqual(m.tz_opt_default, GMT_tz)
        self.assertEqual(m.tz_gmt_offset, UTC_tz)

    def test_invalid_not_blank(self):
        form = TestModelForm({})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('required' in e for e in form.errors['tz']))

    def test_invalid_choice(self):
        form = TestModelForm({'tz': INVALID_TZ})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('choice' in e for e in form.errors['tz']))

    def test_invalid_uncommmon_tz(self):
        form = TestModelForm({'tz': UNCOMMON_TZ})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('choice' in e for e in form.errors['tz']))

    def test_default_human_readable_choices_dont_have_underscores(self):
        form = TestModelForm()
        pst_choice = [c for c in form.fields['tz'].choices if c[0] == PST_tz]
        self.assertEqual(pst_choice[0][1], 'America/Los Angeles')

    def test_display_GMT_offsets(self):
        form = TestModelForm({'tz_gmt_offset': PST_tz})
        c = [c for c in form.fields['tz_gmt_offset'].choices if c[0] == PST_tz]
        self.assertEqual(c[0][1], 'GMT-08:00 America/Los Angeles')


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

    def test_valid_default_values_without_saving_to_db(self):
        m = TestModel(tz=UTC_tz)
        m.full_clean()
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
        m = TestModel(tz=INVALID_TZ)
        self.assertRaises(ValidationError, m.full_clean)

        m = TestModel(tz=4)
        self.assertRaises(ValidationError, m.full_clean)

        m = TestModel(tz=object())
        self.assertRaises(ValidationError, m.full_clean)

    def test_some_positional_args_ok(self):
        TimeZoneField('a verbose name', 'a name', True)

    def test_too_many_positional_args_not_ok(self):
        def createField():
            TimeZoneField('a verbose name', 'a name', True, 42)
        self.assertRaises(ValueError, createField)

    def test_default_human_readable_choices_dont_have_underscores(self):
        m = TestModel(tz=PST_tz)
        self.assertEqual(m.get_tz_display(), 'America/Los Angeles')


class TimeZoneFieldLimitedChoicesTestCase(TestCase):

    invalid_superset_tz = 'not a tz'
    invalid_subset_tz = 'Europe/Brussels'

    class TestModelChoice(models.Model):
        tz_superset = TimeZoneField(
            choices=[(tz, tz) for tz in pytz.all_timezones],
            blank=True,
        )
        tz_subset = TimeZoneField(
            choices=[(tz, tz) for tz in USA_TZS],
            blank=True,
        )

    class TestModelOldChoiceFormat(models.Model):
        tz_superset = TimeZoneField(
            choices=[(pytz.timezone(tz), tz) for tz in pytz.all_timezones],
            blank=True,
        )
        tz_subset = TimeZoneField(
            choices=[(pytz.timezone(tz), tz) for tz in USA_TZS],
            blank=True,
        )

    def test_valid_choice(self):
        self.TestModelChoice.objects.create(tz_superset=PST, tz_subset=PST)
        m = self.TestModelChoice.objects.get()
        self.assertEqual(m.tz_superset, PST_tz)
        self.assertEqual(m.tz_subset, PST_tz)

    def test_invalid_choice(self):
        m = self.TestModelChoice(tz_superset=self.invalid_superset_tz)
        self.assertRaises(ValidationError, m.full_clean)

        m = self.TestModelChoice(tz_subset=self.invalid_subset_tz)
        self.assertRaises(ValidationError, m.full_clean)

    def test_valid_choice_old_format(self):
        self.TestModelOldChoiceFormat.objects.create(
            tz_superset=PST, tz_subset=PST,
        )
        m = self.TestModelOldChoiceFormat.objects.get()
        self.assertEqual(m.tz_superset, PST_tz)
        self.assertEqual(m.tz_subset, PST_tz)

    def test_invalid_choice_old_format(self):
        m = self.TestModelOldChoiceFormat(tz_superset=self.invalid_superset_tz)
        self.assertRaises(ValidationError, m.full_clean)

        m = self.TestModelOldChoiceFormat(tz_subset=self.invalid_subset_tz)
        self.assertRaises(ValidationError, m.full_clean)


class TimeZoneFieldDeconstructTestCase(TestCase):

    test_fields = (
        TimeZoneField(),
        TimeZoneField(default='UTC'),
        TimeZoneField(max_length=42),
        TimeZoneField(choices=[
            (pytz.timezone('US/Pacific'), 'US/Pacific'),
            (pytz.timezone('US/Eastern'), 'US/Eastern'),
        ]),
        TimeZoneField(choices=[
            (pytz.timezone(b'US/Pacific'), b'US/Pacific'),
            (pytz.timezone(b'US/Eastern'), b'US/Eastern'),
        ]),
        TimeZoneField(choices=[
            ('US/Pacific', 'US/Pacific'),
            ('US/Eastern', 'US/Eastern'),
        ]),
        TimeZoneField(choices=[
            (b'US/Pacific', b'US/Pacific'),
            (b'US/Eastern', b'US/Eastern'),
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

    def test_from_db_value(self):
        """
        Verify that the field can handle data coming back as bytes from the
        db.
        """
        field = TimeZoneField()

        # django 1.11 signuature
        value = field.from_db_value(b'UTC', None, None, None)
        self.assertEqual(pytz.UTC, value)

        # django 2.0+ signuature
        value = field.from_db_value(b'UTC', None, None)
        self.assertEqual(pytz.UTC, value)

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

        choices = [
            (pytz.timezone(tz), tz.replace('_', ' '))
            for tz in pytz.common_timezones
        ]
        field = TimeZoneField(choices=choices)
        name, path, args, kwargs = field.deconstruct()
        self.assertNotIn('choices', kwargs)

        choices = [(tz, tz.replace('_', ' ')) for tz in pytz.common_timezones]
        field = TimeZoneField(choices=choices)
        name, path, args, kwargs = field.deconstruct()
        self.assertNotIn('choices', kwargs)


class GmtOffsetInChoicesTestCase(TestCase):

    # test timezones out of order, but they should appear in order in result.
    timezones = [
        (pytz.timezone('US/Eastern'), 'US/Eastern'),
        (pytz.timezone('US/Pacific'), 'US/Pacific'),
        (pytz.timezone('Asia/Qatar'), 'Asia/Qatar'),
        (pytz.timezone('Pacific/Fiji'), 'Pacific/Fiji'),
        (pytz.timezone('Europe/London'), 'Europe/London'),
        (pytz.timezone('Pacific/Apia'), 'Pacific/Apia'),
    ]

    def test_add_gmt_offset_to_choices(self):
        result = add_gmt_offset_to_choices(self.timezones)
        expected = [
            "GMT-11:00 Pacific/Apia",
            "GMT-08:00 US/Pacific",
            "GMT-05:00 US/Eastern",
            "GMT+00:00 Europe/London",
            "GMT+03:00 Asia/Qatar",
            "GMT+13:00 Pacific/Fiji",
        ]
        for i in range(len(expected)):
            self.assertEqual(expected[i], result[i][1])


class TimeZoneSerializer(serializers.Serializer):
    tz = TimeZoneSerializerField()


class TimeZoneSerializerFieldTestCase(TestCase):
    def test_invalid_str(self):
        serializer = TimeZoneSerializer(data={'tz': INVALID_TZ})
        self.assertFalse(serializer.is_valid())

    def test_valid(self):
        serializer = TimeZoneSerializer(data={'tz': PST})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['tz'], PST_tz)

    def test_valid_representation(self):
        serializer = TimeZoneSerializer(data={'tz': PST})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['tz'], PST)

    def test_valid_with_timezone_object(self):
        serializer = TimeZoneSerializer(data={'tz': PST_tz})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data['tz'], PST)
        self.assertEqual(serializer.validated_data['tz'], PST_tz)
