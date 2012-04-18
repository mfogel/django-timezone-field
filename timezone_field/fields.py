import pytz

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_unicode

from timezone_field.validators import TzMaxLengthValidator


class TimeZoneField(models.Field):
    """
    A TimeZoneField stores pytz DstTzInfo objects to the database.

    Examples of valid inputs:
        ''                          # if blank == True
        'America/Los_Angles'        # validated against pytz.all_timezones
        None                        # if blank == True
        pytz.tzinfo.DstTzInfo       # an instance of

    Note that blank values ('' and None) are stored as an empty string
    in the db. Specifiying null=True makes your db column not have a NOT
    NULL constraint, but from the perspective of this field, has no effect.

    If you choose to add validators at runtime, they need to accept
    pytz.tzinfo.DstTzInfo objects as input.
    """

    description = "A pytz.tzinfo.DstTzInfo object"

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
        "Returns pytz.tzinfo objects"
        # inspriation from django's Datetime field
        if value is None or value == '':
            return None
        if isinstance(value, pytz.tzinfo.DstTzInfo):
            return value
        if isinstance(value, basestring):
            try:
                return pytz.timezone(value)
            except pytz.UnknownTimeZoneError:
                pass
        raise ValidationError("Invalid timezone '{}'".format(value))

    def get_prep_value(self, value):
        "Accepts both a pytz.info object or a string representing a timezone"
        # inspriation from django's Datetime field
        value = self.to_python(value)
        if value is None:
            return ''
        if isinstance(value, pytz.tzinfo.DstTzInfo):
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
