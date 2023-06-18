import pytest
from rest_framework import serializers

from timezone_field.rest_framework import TimeZoneSerializerField


@pytest.fixture
def TimeZoneSerializer(use_pytz):
    class _TimeZoneSerializer(serializers.Serializer):
        # pylint: disable=abstract-method
        tz = TimeZoneSerializerField(use_pytz=use_pytz)

    yield _TimeZoneSerializer


def test_invalid_str(TimeZoneSerializer, invalid_tz):
    serializer = TimeZoneSerializer(data={"tz": invalid_tz})
    assert not serializer.is_valid()


# https://github.com/mfogel/django-timezone-field/issues/86
def test_empty_str(TimeZoneSerializer, invalid_tz):
    serializer = TimeZoneSerializer(data={"tz": ""})
    assert not serializer.is_valid()


def test_valid(TimeZoneSerializer, pst, pst_tz):
    serializer = TimeZoneSerializer(data={"tz": pst})
    assert serializer.is_valid()
    assert serializer.validated_data["tz"] == pst_tz


def test_valid_representation(TimeZoneSerializer, pst):
    serializer = TimeZoneSerializer(data={"tz": pst})
    assert serializer.is_valid()
    assert serializer.data["tz"] == pst


def test_valid_with_timezone_object(TimeZoneSerializer, pst, pst_tz):
    serializer = TimeZoneSerializer(data={"tz": pst_tz})
    assert serializer.is_valid()
    assert serializer.data["tz"] == pst
    assert serializer.validated_data["tz"] == pst_tz
