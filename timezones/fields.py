
from django.db import models
from django.conf import settings
from django.utils.encoding import smart_unicode, smart_str

from timezones import forms

MAX_TIMEZONE_LENGTH = getattr(settings, 'MAX_TIMEZONE_LENGTH', 100)

assert(all(len(x) <= MAX_TIMEZONE_LENGTH for x in forms.TIMEZONE_CHOICES),
       "timezones.fields.TimeZoneField MAX_TIMEZONE_LENGTH is too small")

class TimeZoneField(models.CharField):

    def __init__(self, *args, **kwdargs):
        defaults = {'max_length': MAX_TIMEZONE_LENGTH,
                    'default': settings.TIME_ZONE,
                    'choices': forms.TIMEZONE_CHOICES}
        defaults.update(kwdargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)

    def to_python(self, value):
        value = super(TimeZoneField, self).to_python(value)
        if value is None: return None # null=True
        return pytz.timezone(value)

    def get_db_prep_save(self, value):
        # Casts timezone into string format for entry into database.
        if value is not None:
            value = smart_unicode(value)
        return super(TimeZoneField, self).get_db_prep_save(value)

    def flatten_data(self, follow, obj=None):
        val = self._get_val_from_obj(obj)
        if val is None: val = ''
        return {self.attname: smart_unicode(val)}

    def formfield(self, **kwdargs):
        defaults = {"form_class": forms.TimeZoneField}
        defaults.update(kwdargs)
        return super(TimeZoneField, self).formfield(**defaults)

class LocalizedDateTimeField(models.DateTimeField):
    """
    A model field that provides automatic integration with a ModelForm.
    """
    def formfield(self, **kwargs):
        defaults = {"form_class": forms.LocalizedDateTimeField}
        defaults.update(kwargs)
        return super(LocalizedDateTime, self).formfield(**defaults)
