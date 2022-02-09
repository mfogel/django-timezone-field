import pytest
import pytz
from django.db.migrations.writer import MigrationWriter

from timezone_field import TimeZoneField
from timezone_field.compat import ZoneInfo

test_fields = [
    TimeZoneField(),
    TimeZoneField(default="UTC"),
    TimeZoneField(max_length=42),
    TimeZoneField(use_pytz=True),
    TimeZoneField(use_pytz=False),
    TimeZoneField(choices=[("US/Pacific", "US/Pacific"), ("US/Eastern", "US/Eastern")]),
    TimeZoneField(choices=[(b"US/Pacific", b"US/Pacific"), (b"US/Eastern", b"US/Eastern")]),
    TimeZoneField(
        choices=[(pytz.timezone("US/Pacific"), "US/Pacific"), (pytz.timezone("US/Eastern"), "US/Eastern")],
        use_pytz=True,
    ),
    TimeZoneField(
        choices=[(ZoneInfo("US/Pacific"), "US/Pacific"), (ZoneInfo("US/Eastern"), "US/Eastern")],
        use_pytz=False,
    ),
]


@pytest.mark.parametrize("field", test_fields)
def test_deconstruct(field):
    _name, _path, args, kwargs = field.deconstruct()
    new_field = TimeZoneField(*args, **kwargs)
    assert field.max_length == new_field.max_length
    assert field.choices == new_field.choices


@pytest.mark.parametrize("field", test_fields)
def test_full_serialization(field):
    # ensure the values passed to kwarg arguments can be serialized
    # the recommended 'deconstruct' testing by django docs doesn't cut it
    # https://docs.djangoproject.com/en/1.7/howto/custom-model-fields/#field-deconstruction
    # replicates https://github.com/mfogel/django-timezone-field/issues/12
    MigrationWriter.serialize(field)  # should not throw


def test_from_db_value(use_pytz):
    """
    Verify that the field can handle data coming back as bytes from the
    db.
    """
    field = TimeZoneField(use_pytz=use_pytz)
    utc = pytz.UTC if use_pytz else ZoneInfo("UTC")
    value = field.from_db_value(b"UTC", None, None)
    assert utc == value


def test_default_kwargs_not_frozen():
    """
    Ensure the deconstructed representation of the field does not contain
    kwargs if they match the default.
    Don't want to bloat everyone's migration files.
    """
    field = TimeZoneField()
    _name, _path, _args, kwargs = field.deconstruct()
    assert "choices" not in kwargs
    assert "max_length" not in kwargs


def test_specifying_defaults_not_frozen():
    """
    If someone's matched the default values with their kwarg args, we
    shouldn't bothering freezing those
    (excluding the use_pytz, which changes with your django version).
    """
    field = TimeZoneField(max_length=63)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "max_length" not in kwargs

    choices = [(tz, tz.replace("_", " ")) for tz in pytz.common_timezones]
    field = TimeZoneField(choices=choices)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "choices" not in kwargs

    choices = [(pytz.timezone(tz), tz.replace("_", " ")) for tz in pytz.common_timezones]
    field = TimeZoneField(choices=choices, use_pytz=True)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "choices" not in kwargs

    choices = [(ZoneInfo(tz), tz.replace("_", " ")) for tz in pytz.common_timezones]
    field = TimeZoneField(choices=choices, use_pytz=False)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "choices" not in kwargs


@pytest.mark.parametrize(
    "choices, use_pytz",
    [
        [
            [("US/Pacific", "US/Pacific"), ("US/Eastern", "US/Eastern")],
            None,
        ],
        [
            [(pytz.timezone("US/Pacific"), "US/Pacific"), (pytz.timezone("US/Eastern"), "US/Eastern")],
            True,
        ],
        [
            [(ZoneInfo("US/Pacific"), "US/Pacific"), (ZoneInfo("US/Eastern"), "US/Eastern")],
            False,
        ],
    ],
)
def test_deconstruct_when_using_choices(choices, use_pytz):
    field = TimeZoneField(choices=choices, use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs == {
        **{
            "choices": [
                ("US/Pacific", "US/Pacific"),
                ("US/Eastern", "US/Eastern"),
            ]
        },
        **({"use_pytz": use_pytz} if use_pytz is not None else {}),
    }


@pytest.mark.parametrize(
    "choices_display, expected_kwargs",
    [
        [None, {}],
        ["STANDARD", {"choices_display": "STANDARD"}],
        ["WITH_GMT_OFFSET", {"choices_display": "WITH_GMT_OFFSET"}],
    ],
)
def test_deconstruct_when_using_choices_display(choices_display, expected_kwargs):
    field = TimeZoneField(choices_display=choices_display)
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
def test_deconstruct_when_using_choices_and_choices_display(choices, choices_display, expected_kwargs):
    field = TimeZoneField(choices=choices, choices_display=choices_display)
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs == expected_kwargs


@pytest.mark.parametrize(
    "use_pytz, expected_kwargs",
    [
        [None, {}],
        [True, {"use_pytz": True}],
        [False, {"use_pytz": False}],
    ],
)
def test_deconstruct_when_using_use_pytz(use_pytz, expected_kwargs):
    field = TimeZoneField(use_pytz=use_pytz)
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs == expected_kwargs
