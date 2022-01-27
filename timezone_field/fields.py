import django
import pytz
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_str

from timezone_field import compat
from timezone_field.choices import standard, with_gmt_offset
from timezone_field.utils import add_gmt_offset_to_choices, is_pytz_instance, is_tzinfo_instance

use_tzinfo = django.VERSION >= (4, 0)

default_pytz_tzs = [pytz.timezone(tz) for tz in pytz.common_timezones]
default_pytz_choices = standard(default_pytz_tzs)
default_zoneinfo_tzs = compat.get_default_zoneinfo_tzs()
default_zoneinfo_choices = standard(default_zoneinfo_tzs)


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

    description = "A timezone object"

    # NOTE: these defaults are excluded from migrations. If these are changed,
    #       existing migration files will need to be accomodated.
    default_max_length = 63

    def __init__(self, *args, **kwargs):
        # allow some use of positional args up until the args we customize
        # https://github.com/mfogel/django-timezone-field/issues/42
        # https://github.com/django/django/blob/1.11.11/django/db/models/fields/__init__.py#L145
        if len(args) > 3:
            raise ValueError("Cannot specify max_length by positional arg")
        kwargs.setdefault("max_length", self.default_max_length)
        self.use_pytz = kwargs.pop("use_pytz", not use_tzinfo)

        if not self.use_pytz and kwargs.get("display_GMT_offset"):
            raise ValueError("Cannot use ZoneInfo based timezones and display_GMT_offset")

        self.default_tzs = default_pytz_tzs if self.use_pytz else default_zoneinfo_tzs
        self.default_choices = default_pytz_choices if self.use_pytz else default_zoneinfo_choices

        if kwargs.get("choices"):
            values, displays = zip(*kwargs["choices"])
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
            if self.use_pytz and not is_pytz_instance(values[0]):
                values = [pytz.timezone(v) for v in values]
            elif not self.use_pytz and not is_tzinfo_instance(values[0]):
                values = [compat.to_zoneinfo(force_str(v)) for v in values]
        else:
            values = self.default_tzs
            displays = None

        self.choices_display = kwargs.pop("choices_display", None)
        if self.choices_display == "WITH_GMT_OFFSET":
            choices = with_gmt_offset(values)
        elif self.choices_display == "STANDARD":
            choices = standard(values)
        elif self.choices_display is None:
            choices = zip(values, displays) if displays else standard(values)
        else:
            raise ValueError("Unrecognized value for kwarg 'choices_display' of '" + self.choices_display + "'")

        # 'display_GMT_offset' is deprecated, use 'choices_display' instead
        if kwargs.pop("display_GMT_offset", False):
            choices = add_gmt_offset_to_choices(choices)

        kwargs["choices"] = choices
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        if (self.use_pytz and not is_pytz_instance(value)) or (not self.use_pytz and not is_tzinfo_instance(value)):
            raise ValidationError("'%s' is not a pytz timezone object" % value)
        super().validate(value, model_instance)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_length") == self.default_max_length:
            del kwargs["max_length"]

        if self.choices_display is not None:
            kwargs["choices_display"] = self.choices_display

        choices = kwargs.get("choices")
        if choices:
            if self.choices_display is None:
                defaults = [default_pytz_choices]
                if default_zoneinfo_tzs:
                    defaults += [default_zoneinfo_choices]
                if choices == self.default_choices:
                    kwargs.pop("choices")
            else:
                values, _ = zip(*choices)
                defaults = [default_pytz_tzs]
                if default_zoneinfo_tzs:
                    defaults += [default_zoneinfo_tzs]
                if sorted(values, key=str) in defaults:
                    kwargs.pop("choices")
                else:
                    kwargs["choices"] = [(value, "") for value in values]

        # django can't decontruct pytz objects, so transform choices
        # to [<str>, <str>] format for writing out to the migration
        if kwargs.get("choices"):
            kwargs["choices"] = [(str(tz), n) for tz, n in kwargs["choices"]]
        return name, path, args, kwargs

    def get_internal_type(self):
        return "CharField"

    def get_default(self):
        # allow defaults to be still specified as strings. Allows for easy
        # serialization into migration files
        value = super().get_default()
        return self._get_python_and_db_repr(value)[0]

    def from_db_value(self, value, *_args):
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
        if value is None or value == "":
            return (None, "")
        if self.use_pytz:
            if is_pytz_instance(value):
                return (value, value.zone)
            try:
                return (pytz.timezone(force_str(value)), force_str(value))
            except pytz.UnknownTimeZoneError:
                pass
        else:
            if compat.is_zoneinfo_instance(value):
                return (value, value.key)
            try:
                return (compat.to_zoneinfo(value), force_str(value))
            except compat.ZoneInfoNotFoundError:
                pass
        raise ValidationError("Invalid timezone '%s'" % value)
