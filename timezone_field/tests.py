import pytz

from django import forms
from django.db import models
from django.test import TestCase

from timezone_field.fields import TimeZoneField


PST = 'America/Los_Angeles'
EST = 'America/New_York'


class TestModel(models.Model):
    timezone = TimeZoneField()


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class TimeZoneFieldTestCase(TestCase):

    def test_models_modelform_validation(self):
        form = TestModelForm({'timezone': PST})
        self.assertTrue(form.is_valid())

    def test_models_modelform_save(self):
        form = TestModelForm({'timezone': EST})
        self.assertTrue(form.is_valid())
        form.save()

    def test_models_string_value(self):
        p = TestModel(timezone=PST)
        p.save()
        p = TestModel.objects.get(pk=p.pk)
        self.assertEqual(p.timezone, pytz.timezone(PST))

    def test_models_string_value_lookup(self):
        TestModel(timezone=EST).save()
        qs = TestModel.objects.filter(timezone=EST)
        self.assertEqual(qs.count(), 1)

    def test_models_tz_value(self):
        tz = pytz.timezone(PST)
        p = TestModel(timezone=tz)
        p.save()
        p = TestModel.objects.get(pk=p.pk)
        self.assertEqual(p.timezone, tz)

    def test_models_tz_value_lookup(self):
        TestModel(timezone=PST).save()
        qs = TestModel.objects.filter(timezone=pytz.timezone(PST))
        self.assertEqual(qs.count(), 1)
