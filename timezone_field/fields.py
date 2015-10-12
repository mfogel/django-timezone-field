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

    Blank values are stored as null in the DB, not the empty string.
    Thus, by default the database column does not have a NOT NULL constraint.
    Note this is different than the default beahvior of django's CharField.

    If you choose to override the 'choices' kwarg argument, and you specify
    choices that can't be consumed by pytz.timezone(unicode(YOUR_NEW_CHOICE)),
    weirdness will ensue. It's ok to further limit CHOICES, but not expand it.
    """

    description = "A pytz timezone object"

    # NOTE: these defaults are excluded from migrations. If these are changed,
    #       existing migration files will need to be accomodated.
    CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.common_timezones]
    MAX_LENGTH = 63

    def __init__(self, choices=None, max_length=None, null=None, **kwargs):
        if choices is not None:

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
            if isinstance(choices[0][0], six.string_types):
                choices = [(pytz.timezone(n1), n2) for n1, n2 in choices]

        kwargs['choices'] = choices or self.CHOICES
        kwargs['max_length'] = max_length or self.MAX_LENGTH
        kwargs['null'] = null if null is not None else True

        super(TimeZoneFieldBase, self).__init__(**kwargs)

    def validate(self, value, model_instance):
        if not is_pytz_instance(value):
            raise ValidationError("'%s' is not a pytz timezone object" % value)
        super(TimeZoneFieldBase, self).validate(value, model_instance)

    def deconstruct(self):
        name, path, args, kwargs = super(TimeZoneFieldBase, self).deconstruct()
        if kwargs['choices'] == self.CHOICES:
            del kwargs['choices']
        if kwargs['max_length'] == self.MAX_LENGTH:
            del kwargs['max_length']

        # django can't decontruct pytz objects, so transform choices
        # to [<str>, <str>] format for writing out to the migration
        if 'choices' in kwargs:
            kwargs['choices'] = [(tz.zone, n) for tz, n in kwargs['choices']]

        # there was an unfortunate historical choice to make the default
        # for this field null=True, rather than follow the default null=False
        # The parent field's deconstruct() automatically strips null=False
        # out of kwargs - so we have to add it back in here, and remove our
        # default of null=True
        #
        # Note that if a django-timezone-field 2.0 is ever released, this
        # default # value for the null kwarg will probably be switched over
        # to False (and the empty string would be used at the DB level to
        # represent the 'no timezone' case).
        if 'null' in kwargs and kwargs['null']:
            # our default of True, strip it out
            del kwargs['null']
        else:
            # django default, add it back
            kwargs['null'] = False

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
