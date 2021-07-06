import pytest
import pytz

from django.db.migrations.writer import MigrationWriter

from timezone_field import TimeZoneField


test_fields = (
    TimeZoneField(),
    TimeZoneField(default='UTC'),
    TimeZoneField(max_length=42),
    TimeZoneField(choices=[
        (pytz.timezone('US/Pacific'), 'US/Pacific'),
        (pytz.timezone('US/Eastern'), 'US/Eastern'),
    ]),
    TimeZoneField(choices=[
        (pytz.timezone(b'US/Pacific'), b'US/Pacific'),
        (pytz.timezone(b'US/Eastern'), b'US/Eastern'),
    ]),
    TimeZoneField(choices=[
        ('US/Pacific', 'US/Pacific'),
        ('US/Eastern', 'US/Eastern'),
    ]),
    TimeZoneField(choices=[
        (b'US/Pacific', b'US/Pacific'),
        (b'US/Eastern', b'US/Eastern'),
    ]),
)


def test_deconstruct():
    for org_field in test_fields:
        name, path, args, kwargs = org_field.deconstruct()
        new_field = TimeZoneField(*args, **kwargs)
        assert org_field.max_length == new_field.max_length
        assert org_field.choices == new_field.choices


def test_full_serialization():
    # ensure the values passed to kwarg arguments can be serialized
    # the recommended 'deconstruct' testing by django docs doesn't cut it
    # https://docs.djangoproject.com/en/1.7/howto/custom-model-fields/#field-deconstruction
    # replicates https://github.com/mfogel/django-timezone-field/issues/12
    for field in test_fields:
        # ensuring the following call doesn't throw an error
        MigrationWriter.serialize(field)


def test_from_db_value():
    """
    Verify that the field can handle data coming back as bytes from the
    db.
    """
    field = TimeZoneField()

    # django 1.11 signuature
    value = field.from_db_value(b'UTC', None, None, None)
    assert pytz.UTC == value

    # django 2.0+ signuature
    value = field.from_db_value(b'UTC', None, None)
    assert pytz.UTC == value


def test_default_kwargs_not_frozen():
    """
    Ensure the deconstructed representation of the field does not contain
    kwargs if they match the default.
    Don't want to bloat everyone's migration files.
    """
    field = TimeZoneField()
    name, path, args, kwargs = field.deconstruct()
    assert 'choices' not in kwargs
    assert 'max_length' not in kwargs


def test_specifying_defaults_not_frozen():
    """
    If someone's matched the default values with their kwarg args, we
    shouldn't bothering freezing those.
    """
    field = TimeZoneField(max_length=63)
    name, path, args, kwargs = field.deconstruct()
    assert 'max_length' not in kwargs

    choices = [
        (pytz.timezone(tz), tz.replace('_', ' '))
        for tz in pytz.common_timezones
    ]
    field = TimeZoneField(choices=choices)
    name, path, args, kwargs = field.deconstruct()
    assert 'choices' not in kwargs

    choices = [(tz, tz.replace('_', ' ')) for tz in pytz.common_timezones]
    field = TimeZoneField(choices=choices)
    name, path, args, kwargs = field.deconstruct()
    assert 'choices' not in kwargs


@pytest.mark.parametrize('choices', [[
    (pytz.timezone('US/Pacific'), 'US/Pacific'),
    (pytz.timezone('US/Eastern'), 'US/Eastern'),
], [
    ('US/Pacific', 'US/Pacific'),
    ('US/Eastern', 'US/Eastern'),
]])
def test_deconstruct_when_using_just_choices(choices):
    field = TimeZoneField(choices=choices)
    name, path, args, kwargs = field.deconstruct()
    assert kwargs == {'choices': [
        ('US/Pacific', 'US/Pacific'),
        ('US/Eastern', 'US/Eastern'),
    ]}


@pytest.mark.parametrize('choices_display, expected_kwargs', [
    [None, {}],
    ['STANDARD', {'choices_display': 'STANDARD'}],
    ['WITH_GMT_OFFSET', {'choices_display': 'WITH_GMT_OFFSET'}],
])
def test_deconstruct_when_using_just_choices_display(choices_display, expected_kwargs):
    field = TimeZoneField(choices_display=choices_display)
    name, path, args, kwargs = field.deconstruct()
    assert kwargs == expected_kwargs


@pytest.mark.parametrize('choices, choices_display, expected_kwargs', [
    [
        [['US/Pacific', 'West Coast Time']],
        None,
        {'choices': [('US/Pacific', 'West Coast Time')]},
    ],
    [
        [['US/Pacific', 'West Coast Time']],
        'STANDARD',
        {'choices': [('US/Pacific', '')], 'choices_display': 'STANDARD'},
    ],
    [
        [['US/Pacific', 'West Coast Time']],
        'WITH_GMT_OFFSET',
        {'choices': [('US/Pacific', '')], 'choices_display': 'WITH_GMT_OFFSET'},
    ],
    [
        [[tz, 'ignored'] for tz in pytz.common_timezones],
        'WITH_GMT_OFFSET',
        {'choices_display': 'WITH_GMT_OFFSET'},
    ],
])
def test_deconstruct_when_using_choices_and_choices_display(
        choices, choices_display, expected_kwargs):
    field = TimeZoneField(choices=choices, choices_display=choices_display)
    name, path, args, kwargs = field.deconstruct()
    assert kwargs == expected_kwargs
