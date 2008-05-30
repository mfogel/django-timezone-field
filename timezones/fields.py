
from django.db import models

from timezones import forms

class LocalizedDateTimeField(models.CharField):
    def formfield(self, **kwargs):
        defaults = {"form_class": forms.LocalizedDateTimeField}
        defaults.update(kwargs)
        return super(LocalizedDateTime, self).formfield(**defaults)
