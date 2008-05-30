
from django.db import models

from timezones import forms

class LocalizedDateTimeField(models.DateTimeField):
    """
    A model field that provides automatic integration with a ModelForm.
    """
    def formfield(self, **kwargs):
        defaults = {"form_class": forms.LocalizedDateTimeField}
        defaults.update(kwargs)
        return super(LocalizedDateTime, self).formfield(**defaults)
