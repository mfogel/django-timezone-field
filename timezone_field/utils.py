from django.core.exceptions import ValidationError

import pytz


def coerce_timezone_value(value):
    try:
        return pytz.timezone(value)
    except pytz.UnknownTimeZoneError:
        raise ValidationError("Unknown timezone")


def validate_timezone_max_length(max_length, zones):
    def reducer(x, y):
        return x and (len(y) <= max_length)
    if not reduce(reducer, zones, True):
        raise Exception("timezone_field.fields.TimeZoneField MAX_TIMEZONE_LENGTH is too small")
