import pytest
import pytz
from django.db.migrations.writer import MigrationWriter

from timezone_field import TimeZoneField
from timezone_field.compat import ZoneInfo


@pytest.fixture
def fields(use_pytz):
    return (
        TimeZoneField(use_pytz=use_pytz),
        TimeZoneField(default="UTC", use_pytz=use_pytz),
        TimeZoneField(max_length=42, use_pytz=use_pytz),
        TimeZoneField(
            choices=[
                (pytz.timezone("US/Pacific"), "US/Pacific"),
                (pytz.timezone("US/Eastern"), "US/Eastern"),
            ],
            use_pytz=use_pytz,
        ),
        TimeZoneField(
            choices=[
                (pytz.timezone(b"US/Pacific"), b"US/Pacific"),
                (pytz.timezone(b"US/Eastern"), b"US/Eastern"),
            ],
            use_pytz=use_pytz,
        ),
        TimeZoneField(
            choices=[
                ("US/Pacific", "US/Pacific"),
                ("US/Eastern", "US/Eastern"),
            ],
            use_pytz=use_pytz,
        ),
        TimeZoneField(
            choices=[
                (b"US/Pacific", b"US/Pacific"),
                (b"US/Eastern", b"US/Eastern"),
            ],
            use_pytz=use_pytz,
        ),
    )


def test_deconstruct(fields, use_pytz):
    if not use_pytz:
        fields += (
            TimeZoneField(
                choices=[
                    (ZoneInfo("US/Pacific"), "US/Pacific"),
                    (ZoneInfo("US/Eastern"), "US/Eastern"),
                ],
                use_pytz=use_pytz,
            ),
        )
    for org_field in fields:
        _name, _path, args, kwargs = org_field.deconstruct()
        new_field = TimeZoneField(*args, use_pytz=use_pytz, **kwargs)
        assert org_field.max_length == new_field.max_length
        assert org_field.choices == new_field.choices


def test_full_serialization(fields):
    # ensure the values passed to kwarg arguments can be serialized
    # the recommended 'deconstruct' testing by django docs doesn't cut it
    # https://docs.djangoproject.com/en/1.7/howto/custom-model-fields/#field-deconstruction
    # replicates https://github.com/mfogel/django-timezone-field/issues/12
    for field in fields:
        # ensuring the following call doesn't throw an error
        MigrationWriter.serialize(field)


def test_from_db_value(use_pytz):
    """
    Verify that the field can handle data coming back as bytes from the
    db.
    """
    field = TimeZoneField(use_pytz=use_pytz)
    utc = pytz.UTC if use_pytz else ZoneInfo("UTC")
    value = field.from_db_value(b"UTC", None, None)
    assert utc == value


def test_default_kwargs_not_frozen(use_pytz):
    """
    Ensure the deconstructed representation of the field does not contain
    kwargs if they match the default.
    Don't want to bloat everyone's migration files.
    """
    field = TimeZoneField(use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "choices" not in kwargs
    assert "max_length" not in kwargs


def test_specifying_defaults_not_frozen(use_pytz, tz_func):
    """
    If someone's matched the default values with their kwarg args, we
    shouldn't bothering freezing those.
    """
    field = TimeZoneField(max_length=63, use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "max_length" not in kwargs

    choices = [(tz_func(tz), tz.replace("_", " ")) for tz in pytz.common_timezones]
    field = TimeZoneField(choices=choices, use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "choices" not in kwargs

    choices = [(tz, tz.replace("_", " ")) for tz in pytz.common_timezones]
    field = TimeZoneField(choices=choices, use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "choices" not in kwargs


@pytest.mark.parametrize(
    "use_tz_object, timezones",
    [
        [True, ["US/Pacific", "US/Eastern"]],
        [False, ["US/Pacific", "US/Eastern"]],
    ],
)
def test_deconstruct_when_using_just_choices(use_tz_object, timezones, use_pytz, tz_func):
    if not use_tz_object:
        tz_func = str
    choices = [(tz_func(tz), tz) for tz in timezones]
    field = TimeZoneField(choices=choices, use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs == {
        "choices": [
            ("US/Pacific", "US/Pacific"),
            ("US/Eastern", "US/Eastern"),
        ]
    }


@pytest.mark.parametrize(
    "choices_display, expected_kwargs",
    [
        [None, {}],
        ["STANDARD", {"choices_display": "STANDARD"}],
        ["WITH_GMT_OFFSET", {"choices_display": "WITH_GMT_OFFSET"}],
    ],
)
def test_deconstruct_when_using_just_choices_display(use_pytz, choices_display, expected_kwargs):
    field = TimeZoneField(choices_display=choices_display, use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs == expected_kwargs


@pytest.mark.parametrize(
    "choices, choices_display, expected_kwargs",
    [
        [
            [["US/Pacific", "West Coast Time"]],
            None,
            {"choices": [("US/Pacific", "West Coast Time")]},
        ],
        [
            [["US/Pacific", "West Coast Time"]],
            "STANDARD",
            {"choices": [("US/Pacific", "")], "choices_display": "STANDARD"},
        ],
        [
            [["US/Pacific", "West Coast Time"]],
            "WITH_GMT_OFFSET",
            {"choices": [("US/Pacific", "")], "choices_display": "WITH_GMT_OFFSET"},
        ],
        [
            [[tz, "ignored"] for tz in pytz.common_timezones],
            "WITH_GMT_OFFSET",
            {"choices_display": "WITH_GMT_OFFSET"},
        ],
    ],
)
def test_deconstruct_when_using_choices_and_choices_display(use_pytz, choices, choices_display, expected_kwargs):
    field = TimeZoneField(choices=choices, choices_display=choices_display, use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs == expected_kwargs
