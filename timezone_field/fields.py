import pytz
import six
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_text

from timezone_field.utils import is_pytz_instance


class CastOnAssignDescriptor(object):
    """
    A property descriptor which ensures that `field.to_python()` is called on _every_ assignment to the field.
    This used to be provided by the `django.db.models.subclassing.Creator` class, which in turn
    was used by the deprecated-in-Django-1.10 `SubfieldBase` class, hence the reimplementation here.
    Copied from https://stackoverflow.com/questions/
    39392343/how-do-i-make-a-custom-model-field-call-to-python-when-the-field-is-accessed-imm
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:  # pragma: no cover
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)


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
    CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.all_timezones]
    MAX_LENGTH = 63

    def __init__(self, choices=None, max_length=None, **kwargs):
        if choices is None:
            choices = self.CHOICES
        else:
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

        if max_length is None:
            max_length = self.MAX_LENGTH

        super(TimeZoneField, self).__init__(choices=choices,
                                            max_length=max_length,
                                            **kwargs)

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

    def from_db_value(self, value, expression, connection, *args):
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
        if isinstance(value, six.string_types):
            try:
                return (pytz.timezone(value), value)
            except pytz.UnknownTimeZoneError:
                pass
        try:
            return (pytz.timezone(force_text(value)), force_text(value))
        except pytz.UnknownTimeZoneError:
            pass
        raise ValidationError("Invalid timezone '%s'" % value)

    def contribute_to_class(self, cls, name, virtual_only=False):
        """
        Cast to the correct value every
        """
        super(TimeZoneField, self).contribute_to_class(cls, name, virtual_only)
        setattr(cls, name, CastOnAssignDescriptor(self))
