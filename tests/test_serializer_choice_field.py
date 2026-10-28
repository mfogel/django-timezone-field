import json

import pytest
from rest_framework import generics, serializers
from rest_framework.test import APIRequestFactory

from timezone_field.rest_framework import TimeZoneSerializerChoiceField, TimeZoneSerializerField


def test_default_choices(use_pytz, base_tzstrs, pst, pst_tz):
    field = TimeZoneSerializerChoiceField(use_pytz=use_pytz)
    assert isinstance(field, serializers.ChoiceField)
    assert list(field.choices) == sorted(base_tzstrs)
    assert field.run_validation(pst) == pst_tz
    assert field.run_validation(pst_tz) == pst_tz
    assert field.to_representation(pst_tz) == pst


def test_restricted_choices(use_pytz, pst, pst_tz):
    field = TimeZoneSerializerChoiceField(choices=[(pst, "Pacific time")], use_pytz=use_pytz)
    assert field.choices == {pst: "Pacific time"}
    assert field.run_validation(pst) == pst_tz
    with pytest.raises(serializers.ValidationError) as error:
        field.run_validation("Europe/London")
    assert error.value.get_codes() == ["invalid_choice"]


def test_timezone_object_choices(use_pytz, pst, pst_tz):
    field = TimeZoneSerializerChoiceField(choices=[(pst_tz, "Pacific time")], use_pytz=use_pytz)
    assert field.run_validation(pst) == pst_tz
    assert field.to_representation(pst_tz) == pst


def test_grouped_choices(use_pytz, pst, pst_tz):
    field = TimeZoneSerializerChoiceField(choices=[("America", [(pst, "Pacific")])], use_pytz=use_pytz)
    assert field.choices == {pst: "Pacific"}
    assert field.run_validation(pst) == pst_tz


def test_empty_choices(use_pytz, pst):
    field = TimeZoneSerializerChoiceField(choices=[], use_pytz=use_pytz)
    assert not field.choices
    with pytest.raises(serializers.ValidationError):
        field.run_validation(pst)


def test_invalid_configured_timezone(use_pytz):
    field = TimeZoneSerializerChoiceField(choices=["not/a/timezone"], use_pytz=use_pytz)
    with pytest.raises(serializers.ValidationError) as error:
        field.run_validation("not/a/timezone")
    assert error.value.get_codes() == ["invalid"]


def test_default_rejects_invalid_timezone(use_pytz):
    with pytest.raises(serializers.ValidationError):
        TimeZoneSerializerChoiceField(use_pytz=use_pytz).run_validation("not/a/timezone")


def test_allowed_empty_values(use_pytz):
    field = TimeZoneSerializerChoiceField(use_pytz=use_pytz, allow_null=True, allow_blank=True)
    assert field.run_validation(None) is None
    assert field.run_validation("") == ""
    assert field.to_representation(None) is None
    assert field.to_representation("") == ""


@pytest.mark.parametrize("value", [None, ""])
def test_rejects_empty_by_default(use_pytz, value):
    with pytest.raises(serializers.ValidationError):
        TimeZoneSerializerChoiceField(use_pytz=use_pytz).run_validation(value)


def test_serializer_roundtrip(use_pytz, pst, pst_tz):
    class TimeZoneSerializer(serializers.Serializer):
        # pylint: disable=abstract-method
        tz = TimeZoneSerializerChoiceField(use_pytz=use_pytz)
        optional_tz = TimeZoneSerializerChoiceField(use_pytz=use_pytz, required=False)

    serializer = TimeZoneSerializer(data={"tz": pst})
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {"tz": pst_tz}
    assert serializer.data == {"tz": pst}


@pytest.mark.parametrize("choice_kind", ["strings", "objects", "grouped_objects"])
def test_options_metadata(use_pytz, pst, pst_tz, choice_kind):
    choices = [(pst, "Pacific time")]
    if choice_kind == "objects":
        choices = [(pst_tz, "Pacific time")]
    elif choice_kind == "grouped_objects":
        choices = [("America", [(pst_tz, "Pacific time")])]

    class TimeZoneSerializer(serializers.Serializer):
        # pylint: disable=abstract-method
        tz = TimeZoneSerializerChoiceField(choices=choices, use_pytz=use_pytz)

    class TimeZoneView(generics.CreateAPIView):
        serializer_class = TimeZoneSerializer

    response = TimeZoneView.as_view()(APIRequestFactory().options("/timezones/", HTTP_ACCEPT="application/json"))
    assert response.status_code == 200
    response.render()
    assert json.loads(response.content)["actions"]["POST"]["tz"]["choices"] == [
        {"value": pst, "display_name": "Pacific time"}
    ]


def test_original_field_stays_unrestricted(use_pytz, pst, pst_tz):
    field = TimeZoneSerializerField(use_pytz=use_pytz)
    assert not isinstance(field, serializers.ChoiceField)
    assert field.run_validation(pst) == pst_tz
