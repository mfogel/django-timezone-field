import pytz

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_unicode

from timezone_field.validators import TzMaxLengthValidator


class TimeZoneField(models.Field):
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
        * the pytz.UTC signleton

    Note that blank values ('' and None) are stored as an empty string
    in the db. Specifying null=True makes your db column not have a NOT
    NULL constraint, but from the perspective of this field, has no effect.

    If you choose to add validators at runtime, they need to accept
    pytz.tzinfo.DstTzInfo and pytz.tzinfo.StaticTzInfo objects as input.

    If you choose to override the 'choices' kwarg argument, and you specify
    choices that can't be consumed by pytz.timezone(unicode(YOUR_NEW_CHOICE)),
    weirdness will ensue. Don't do this. It's okay to further limit CHOICES,
    but not expand it.
    """

    description = "A pytz timezone object"

    __metaclass__ = models.SubfieldBase

    CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.all_timezones]
    MAX_LENGTH = 63

    def __init__(self, validators=[], **kwargs):
        defaults = {
            'max_length': TimeZoneField.MAX_LENGTH,
            'choices': TimeZoneField.CHOICES,
        }
        defaults.update(kwargs)
        super(TimeZoneField, self).__init__(**defaults)
        self.validators.append(TzMaxLengthValidator(self.max_length))

    def get_internal_type(self):
        return 'CharField'

    def validate(self, value, model_instance):
        value = self.to_python(value)
        return super(TimeZoneField, self).validate(value, model_instance)

    def to_python(self, value):
        "Convert to pytz timezone object"
        # inspiration from django's Datetime field
        if value is None or value == '':
            return None
        if isinstance(value, pytz.tzinfo.BaseTzInfo) or isinstance(value, type(pytz.utc)):
            return value
        if isinstance(value, basestring):
            try:
                return pytz.timezone(value)
            except pytz.UnknownTimeZoneError:
                pass
        raise ValidationError("Invalid timezone '{}'".format(value))

    def get_prep_value(self, value):
        "Convert to string describing a valid pytz timezone object"
        # inspiration from django's Datetime field
        value = self.to_python(value)
        if value is None:
            return ''
        if isinstance(value, pytz.tzinfo.BaseTzInfo) or isinstance(value, type(pytz.utc)):
            return smart_unicode(value)

    def value_to_string(self, value):
        return self.get_prep_value(value)


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
                    'max_length', { 'default': TimeZoneField.MAX_LENGTH }
                ],
            },
        )],
        patterns=['timezone_field\.fields\.']
    )
