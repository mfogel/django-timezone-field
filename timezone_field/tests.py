import pytz

from django import forms
from django.db import models
from django.test import TestCase

from timezone_field.fields import TimeZoneField


class TestModel(models.Model):
    timezone = TimeZoneField()

class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class TimeZoneFieldTestCase(TestCase):

    def test_models_modelform_validation(self):
        form = TestModelForm({"timezone": "America/Denver"})
        self.assertTrue(form.is_valid())

    def test_models_modelform_save(self):
        form = TestModelForm({"timezone": "America/Denver"})
        self.assertTrue(form.is_valid())
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
