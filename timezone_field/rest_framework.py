from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField, ChoiceField, to_choices_dict

from timezone_field.backends import TimeZoneNotFoundError, get_tz_backend


class TimeZoneSerializerField(CharField):
    default_error_messages = {
        "invalid": _("A valid timezone is required."),
    }

    def __init__(self, *args, **kwargs):
        self.use_pytz = kwargs.pop("use_pytz", None)
        self.tz_backend = get_tz_backend(use_pytz=self.use_pytz)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        data_str = force_str(data)
        try:
            return self.tz_backend.to_tzobj(data_str)
        except TimeZoneNotFoundError:
            self.fail("invalid")

    def to_representation(self, value):
        return str(value)


def _stringify_choices(choices):
    # OPTIONS metadata must expose JSON-serializable keys, including in groups.
    return [
        (force_str(value), _stringify_choices(label.items()) if isinstance(label, dict) else label)
        for value, label in to_choices_dict(choices).items()
    ]


class TimeZoneSerializerChoiceField(ChoiceField):
    """A timezone field exposing all or a subset of timezones as DRF choices."""

    def __init__(self, choices=None, **kwargs):
        self._timezone_field = TimeZoneSerializerField(use_pytz=kwargs.pop("use_pytz", None))
        if choices is None:
            choices = sorted(self._timezone_field.tz_backend.base_tzstrs)
        super().__init__(choices=_stringify_choices(choices), **kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(force_str(data))
        if value == "":
            return value
        return self._timezone_field.to_internal_value(value)

    def to_representation(self, value):
        if value is None or value == "":
            return value
        return self._timezone_field.to_representation(value)
