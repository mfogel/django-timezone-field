from django import forms
from django.core.exceptions import ValidationError

from django.utils.functional import SimpleLazyObject

from timezone_field.backends import TimeZoneNotFoundError, get_tz_backend
from timezone_field.choices import standard, with_gmt_offset


def get_coerce(tz_backend):
    def coerce(val):
        try:
            return tz_backend.to_tzobj(val)
        except TimeZoneNotFoundError as err:
            raise ValidationError(f"Unknown time zone: '{val}'") from err

    return coerce


class TimeZoneFormField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        self.use_pytz = kwargs.pop("use_pytz", None)
        self.tz_backend = get_tz_backend(self.use_pytz)
        kwargs.setdefault("coerce", get_coerce(self.tz_backend))
        kwargs.setdefault("empty_value", None)

        if "choices" in kwargs:
            self._raw_choices = list(kwargs["choices"])
        else:
            self._raw_choices = None

        self._choices_display = kwargs.pop("choices_display", None)
        if self._choices_display not in (None, "WITH_GMT_OFFSET", "STANDARD"):
            raise ValueError(
                f"Unrecognized value for kwarg 'choices_display' of '{self._choices_display}'"
            )

        kwargs["choices"] = SimpleLazyObject(self._build_choices)
        super().__init__(*args, **kwargs)

    def _build_choices(self):
        if self._raw_choices is not None:
            values, displays = zip(*self._raw_choices)
        else:
            values = self.tz_backend.base_tzstrs
            displays = None

        if self._choices_display == "WITH_GMT_OFFSET":
            choices = with_gmt_offset(values, use_pytz=self.use_pytz)
        elif self._choices_display == "STANDARD":
            choices = standard(values)
        elif self._choices_display is None:
            choices = list(zip(values, displays)) if displays else standard(values)
        else:
            raise ValueError(f"Unrecognized value for kwarg 'choices_display' of '{self._choices_display}'")
        return choices
