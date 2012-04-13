import pytz

from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.utils.encoding import smart_unicode


class TimeZoneField(models.CharField):
    """
    A TimeZoneField stores pytz DstTzInfo objects to the database.

    Examples of valid inputs:
        ''                          # if blank == True
        'America/Los_Angles'        # validated against pytz.all_timezones
        None                        # if blank == True
        pytz.tzinfo.DstTzInfo       # an instance of

    The 'null' kwarg is tied directly to 'blank'.
    If you accept blanks, they will be stored in the DB as null's.
    If you don't accept blanks, the db will be statically typed
    with NOT NULL.

    If you choose to add validators at runtime, they need to accept
    pytz.tzinfo objects as input.
    """

    description = "A pytz.tzinfo.DstTzInfo object"

    __metaclass__ = models.SubfieldBase

    CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    MAX_LENGTH = 63

    def __init__(self, blank=False, validators=[], **kwargs):
        # We're not storing strings, we're storing objects.
        # Tie blank and DB null's together directly.
        if 'null' in kwargs:
            raise TypeError("'null' is an invalid keyword argument")

        defaults = {
            'max_length': TimeZoneField.MAX_LENGTH,
            'choices': TimeZoneField.CHOICES,
            'blank': blank,
            'null': blank,
        }
        defaults.update(kwargs)

        super(TimeZoneField, self).__init__(**defaults)

        # validators our parent (CharField) register aren't going to
        # work right out of the box. They expect a string, while our
        # python type is a pytz.tzinfo
        # So, we'll wrap them in a small conversion object.

        class ValidateTimeZoneAsString(object):
            def __init__(self, org_validator):
                self.org_validator = org_validator
            def __call__(self, timezone):
                self.org_validator(smart_unicode(timezone))

        self.validators = [
            ValidateTimeZoneAsString(validator)
            for validator in self.validators
        ]

        self.validators += validators

    def validate(self, value, model_instance):
        # ensure we can consume the value
        value = self.to_python(value)
        # parent validation works on strings
        str_value = smart_unicode(value)
        return super(TimeZoneField, self).validate(str_value, model_instance)

    def to_python(self, value):
        "Returns pytz.tzinfo objects"
        # inspriation from django's Datetime field
        if value is None or value == '':
            return None
        if isinstance(value, pytz.tzinfo.DstTzInfo):
            return value
        try:
            return pytz.timezone(smart_unicode(value))
        except pytz.UnknownTimeZoneError:
            raise ValidationError("Invalid timezone '{}'".format(value))

    def get_prep_value(self, value):
        "Accepts both a pytz.info object or a string representing a timezone"
        # inspriation from django's Datetime field
        value = self.to_python(value)
        # doing some validation
        if isinstance(value, pytz.tzinfo.DstTzInfo):
            return smart_unicode(value)
        if value is None or value == '':
            return None
        raise IntegrityError("Invalid timezone '{}'".format(value))

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
            }
        )],
        patterns=['timezone_field\.fields\.']
    )
