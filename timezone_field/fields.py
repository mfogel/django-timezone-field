import pytz

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import six

from timezone_field.utils import is_pytz_instance


class TimeZoneFieldBase(models.Field):
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

    Note that blank values ('' and None) are stored as an empty string
    in the db. Specifying null=True makes your db column not have a NOT
    NULL constraint, but from the perspective of this field, has no effect.

    If you choose to override the 'choices' kwarg argument, and you specify
    choices that can't be consumed by pytz.timezone(unicode(YOUR_NEW_CHOICE)),
    weirdness will ensue. It's ok to further limit CHOICES, but not expand it.
    """

    description = "A pytz timezone object"

    # NOTE: these defaults are excluded from migrations. If these are changed,
    #       existing migration files will need to be accomodated.
    CHOICES = [(tz, tz) for tz in pytz.common_timezones]
    MAX_LENGTH = 63

    def __init__(self, **kwargs):
        parent_kwargs = {
            'max_length': self.MAX_LENGTH,
            'choices': TimeZoneField.CHOICES,
        }
        parent_kwargs.update(kwargs)
        super(TimeZoneFieldBase, self).__init__(**parent_kwargs)

        # We expect choices in form [<str>, <str>], but we
        # also support [<pytz.timezone>, <str>], for backwards compatability
        # Our parent saved those in self._choices.
        if self._choices:
            if is_pytz_instance(self._choices[0][0]):
                self._choices = [(tz.zone, name) for tz, name in self._choices]

    def validate(self, value, model_instance):
        # since our choices are of the form [<str>, <str>], convert the
        # incoming value to a string for validation
        if not is_pytz_instance(value):
            raise ValidationError("'%s' is not a pytz timezone object" % value)
        tz_as_str = value.zone
        super(TimeZoneFieldBase, self).validate(tz_as_str, model_instance)

    def deconstruct(self):
        name, path, args, kwargs = super(TimeZoneFieldBase, self).deconstruct()
        if kwargs['choices'] == self.CHOICES:
            del kwargs['choices']
        if kwargs['max_length'] == self.MAX_LENGTH:
            del kwargs['max_length']
        return name, path, args, kwargs

    def get_internal_type(self):
        return 'CharField'

    def to_python(self, value):
        "Convert to pytz timezone object"
        return self._get_python_and_db_repr(value)[0]

    def get_prep_value(self, value):
        "Convert to string describing a valid pytz timezone object"
        return self._get_python_and_db_repr(value)[1]

    def _get_python_and_db_repr(self, value):
        "Returns a tuple of (python representation, db representation)"
        if value is None or value == '':
            return (None, None)
        if is_pytz_instance(value):
            return (value, value.zone)
        if isinstance(value, six.string_types):
            try:
                return (pytz.timezone(value), value)
            except pytz.UnknownTimeZoneError:
                pass
        raise ValidationError("Invalid timezone '%s'" % value)


# http://packages.python.org/six/#six.with_metaclass
class TimeZoneField(six.with_metaclass(models.SubfieldBase,
                                       TimeZoneFieldBase)):
    pass


# South support
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(
        rules=[(
            (TimeZoneField, ),  # Class(es) these apply to
            [],                 # Positional arguments (not used)
            {                   # Keyword argument
                'max_length': [
                    'max_length', {'default': TimeZoneField.MAX_LENGTH},
                ],
            },
        )],
        patterns=['timezone_field\.fields\.']
    )
