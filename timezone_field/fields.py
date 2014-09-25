import pytz

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import six
from django.utils.encoding import smart_text, force_text


class TimeZoneFieldBase(models.Field):
    """
    Provides database store for pytz timezone objects.

    Valid inputs:
        * any instance of pytz.tzinfo.DstTzInfo or pytz.tzinfo.StaticTzInfo
        * the pytz.UTC singleton
        * any string that validates against pytz.all_timezones. pytz will
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

    CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.all_timezones]
    MAX_LENGTH = 63

    def __init__(self, **kwargs):
        defaults = {
            'max_length': self.MAX_LENGTH,
            'choices': TimeZoneField.CHOICES,
        }
        defaults.update(kwargs)
        super(TimeZoneFieldBase, self).__init__(**defaults)

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
        if value is pytz.UTC or isinstance(value, pytz.tzinfo.BaseTzInfo):
            return (value, smart_text(value))
        if isinstance(value, six.string_types):
            try:
                return (pytz.timezone(value), value)
            except pytz.UnknownTimeZoneError:
                pass
        raise ValidationError("Invalid timezone '%s'" % value)


# http://packages.python.org/six/#six.with_metaclass
class TimeZoneField(six.with_metaclass(models.SubfieldBase,
                                       TimeZoneFieldBase)):
    def deconstruct(self):
        # as field attributes, we want to preserve the max_length and if it
        # exists, also the default the user has specified
        keywords = {'max_length': TimeZoneField.MAX_LENGTH}
        if self.default != models.fields.NOT_PROVIDED:
            keywords['default'] = self.default

        # information to recreate the field
        return (
            force_text(self.name, strings_only=True),  # name of the field on
                                                       # the model
            'timezone_field.fields.TimeZoneField',     # import path of the
                                                       # field
            (),                                        # list of positional
                                                       # arguments
            keywords                                   # dict of keyword
                                                       # arguments
        )


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
