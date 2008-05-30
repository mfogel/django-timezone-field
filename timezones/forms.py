
from django import newforms as forms

class LocalizedDateTimeField(forms.DateTimeField):
    def clean(self, value):
        value = super(LocalizedDateTimeField, self).clean(value)
        return value
