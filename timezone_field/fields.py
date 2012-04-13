import datetime
import pytz

from django.db import models
from django.utils.encoding import smart_unicode, smart_str


class TimeZoneField(models.CharField):

    description = "A datetime.tzinfo object"

    __metaclass__ = models.SubfieldBase

    CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 63,
            'choices': TimeZoneField.CHOICES,
        }
        defaults.update(kwargs)
        super(TimeZoneField, self).__init__(*args, **defaults)

    def validate(self, value, model_instance):
        # coerce value back to a string to validate correctly
        return super(TimeZoneField, self).validate(smart_str(value), model_instance)

    def run_validators(self, value):
        # coerce value back to a string to validate correctly
        return super(TimeZoneField, self).run_validators(smart_str(value))

    def to_python(self, value):
        "Returns pytz.tzinfo objects"
        # inspriation from django's Datetime field
        if not value:
            return None
        if isinstance(value, datetime.tzinfo):
            return value
        return pytz.timezone(smart_unicode(value))

    def get_prep_value(self, value):
        "Accepts both a pytz.info object or a string representing a timezone"
        # inspriation from django's Datetime field
        value = self.to_python(value)
        if not value:
            return None
        return smart_unicode(value)

    def flatten_data(self, follow, obj=None):
        value = self._get_val_from_obj(obj)
        if value is None:
            value = ''
        return {self.attname: smart_unicode(value)}
