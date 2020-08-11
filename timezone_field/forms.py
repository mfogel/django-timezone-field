import datetime

import pytz
from django.core.exceptions import ValidationError
from django import forms


class TimeZoneFormField(forms.TypedChoiceField):

    @staticmethod
    def coerce_to_pytz(val):
        try:
            return pytz.timezone(val)
        except pytz.UnknownTimeZoneError:
            raise ValidationError("Unknown time zone: '%s'" % val)

    def __init__(self, *args, **kwargs):
        if kwargs.get('display_GMT_offset', False):
            choices = []
            dt = datetime.datetime.utcnow()
            for tz in pytz.common_timezones:
                a = self.coerce_to_pytz(tz)
                offset = a.utcoffset(dt)
                offset_days = offset.days
                offset_hours = offset_days * 24 + offset.seconds / 3600.0
                name = "{:s} (UTC {:+d}:{:02d})".format(tz.replace('_', ' '),
                                                        int(offset_hours),
                                                        int((offset_hours % 1) * 60))
                choices.append((tz, name))
        else:
            choices = [(tz, tz.replace('_', ' ')) for tz in pytz.common_timezones]

        defaults = {
            'coerce': self.coerce_to_pytz,
            'choices': choices,
            'empty_value': None,
        }
        del kwargs['display_GMT_offset']
        defaults.update(kwargs)
        super(TimeZoneFormField, self).__init__(*args, **defaults)
