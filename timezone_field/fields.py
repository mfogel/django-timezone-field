from datetime import datetime, timedelta, time
import pytz

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import six
from django.utils.encoding import force_text

from timezone_field.utils import is_pytz_instance


class TimeZoneField(models.Field):
    """
    Provides database store for pytz timezone objects.

    Valid inputs:
        * any instance of pytz.tzinfo.DstTzInfo or pytz.tzinfo.StaticTzInfo
        * the pytz.UTC singleton
        * any string that validates against pytz.common_timezones. pytz will
          be used to build a timezone object from the string.
        * None and the empty string both represent 'no timezone'

    Valid outputs:
        * None
        * instances of pytz.tzinfo.DstTzInfo and pytz.tzinfo.StaticTzInfo
        * the pytz.UTC singleton

    Blank values are stored in the DB as the empty string. Timezones are stored
    in their string representation.

    The `choices` kwarg can be specified as a list of either
    [<pytz.timezone>, <str>] or [<str>, <str>]. Internally, it is stored as
    [<pytz.timezone>, <str>].
    """

    description = "A pytz timezone object"

    # NOTE: these defaults are excluded from migrations. If these are changed,
    #       existing migration files will need to be accomodated.
    CHOICES = [
        (pytz.timezone(tz), tz.replace('_', ' '))
        for tz in pytz.common_timezones
    ]
    MAX_LENGTH = 63

    def __init__(self, *args, **kwargs):
        # allow some use of positional args up until the args we customize
        # https://github.com/mfogel/django-timezone-field/issues/42
        # https://github.com/django/django/blob/1.11.11/django/db/models/fields/__init__.py#L145
        if len(args) > 3:
            raise ValueError('Cannot specify max_length by positional arg')

        kwargs.setdefault('choices', self.CHOICES)
        kwargs.setdefault('max_length', self.MAX_LENGTH)
        kwargs.setdefault('display_GMT_offset', False)

        # Choices can be specified in two forms: either
        # [<pytz.timezone>, <str>] or [<str>, <str>]
        #
        # The [<pytz.timezone>, <str>] format is the one we actually
        # store the choices in memory because of
        # https://github.com/mfogel/django-timezone-field/issues/24
        #
        # The [<str>, <str>] format is supported because since django
        # can't deconstruct pytz.timezone objects, migration files must
        # use an alternate format. Representing the timezones as strings
        # is the obvious choice.
        choices = kwargs['choices']
        if isinstance(choices[0][0], (six.string_types, six.binary_type)):
            kwargs['choices'] = [(pytz.timezone(n1), n2) for n1, n2 in choices]

        if kwargs['display_GMT_offset']:
            kwargs['choices'] = self._add_gmt_offset_to_choices(kwargs['choices'])
        kwargs.pop('display_GMT_offset', None)

        super(TimeZoneField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        if not is_pytz_instance(value):
            raise ValidationError("'%s' is not a pytz timezone object" % value)
        super(TimeZoneField, self).validate(value, model_instance)

    def deconstruct(self):
        name, path, args, kwargs = super(TimeZoneField, self).deconstruct()
        if kwargs['choices'] == self.CHOICES:
            del kwargs['choices']
        if kwargs['max_length'] == self.MAX_LENGTH:
            del kwargs['max_length']

        # django can't decontruct pytz objects, so transform choices
        # to [<str>, <str>] format for writing out to the migration
        if 'choices' in kwargs:
            kwargs['choices'] = [(tz.zone, n) for tz, n in kwargs['choices']]

        return name, path, args, kwargs

    def get_internal_type(self):
        return 'CharField'

    def get_default(self):
        # allow defaults to be still specified as strings. Allows for easy
        # serialization into migration files
        value = super(TimeZoneField, self).get_default()
        return self._get_python_and_db_repr(value)[0]

    def from_db_value(self, value, *args):
        "Convert to pytz timezone object"
        return self._get_python_and_db_repr(value)[0]

    def to_python(self, value):
        "Convert to pytz timezone object"
        return self._get_python_and_db_repr(value)[0]

    def get_prep_value(self, value):
        "Convert to string describing a valid pytz timezone object"
        return self._get_python_and_db_repr(value)[1]

    def _get_python_and_db_repr(self, value):
        "Returns a tuple of (python representation, db representation)"
        if value is None or value == '':
            return (None, '')
        if is_pytz_instance(value):
            return (value, value.zone)
        try:
            return (pytz.timezone(force_text(value)), force_text(value))
        except pytz.UnknownTimeZoneError:
            pass
        raise ValidationError("Invalid timezone '%s'" % value)

    def _add_gmt_offset_to_choices(self, timezone_set):
        """
        Currently timezone choices items show up like this:
        'America/New_York'

        But this function formats the choices to display in this format:
        GMT-05:00 America/New_York

        :return:
        A list of tuples in this format:
        (<pytz.timezone>, <str>)
        """
        gmt_timezone = pytz.timezone('Greenwich')
        time_ref = datetime(2000, 1, 1)
        time_zero = gmt_timezone.localize(time_ref)
        _choices = []
        for tz, tz_str in timezone_set:
            # z = pytz.timezone(tz)
            delta = (time_zero - tz.localize(time_ref)).total_seconds()
            h = (datetime.min + timedelta(seconds=delta.__abs__())).hour
            gmt_diff = time(h).strftime('%H:%M')
            pair_one = tz
            pair_two = "GMT{sign}{gmt_diff} {timezone}".format(
                sign="-" if delta < 0 else "+",
                gmt_diff=gmt_diff,
                timezone=tz
            )
            _choices.append((delta, pair_one, pair_two))

        _choices.sort(key=lambda x: x[0])
        choices = [(one, two) for zero, one, two in _choices]
        return choices