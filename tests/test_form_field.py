import pytest
from django import forms
from pytest_lazy_fixtures import lf as lazy_fixture

from timezone_field import TimeZoneFormField


@pytest.fixture
def Form(use_pytz):
    class _Form(forms.Form):
        tz = TimeZoneFormField(use_pytz=use_pytz)
        tz_opt = TimeZoneFormField(required=False, use_pytz=use_pytz)

    yield _Form


@pytest.fixture
def FormInvalidChoice(all_tzstrs, invalid_tz, use_pytz):
    class _FormInvalidChoice(forms.Form):
        tz = TimeZoneFormField(choices=([(tz, tz) for tz in all_tzstrs] + [(invalid_tz, "UTC")]), use_pytz=use_pytz)

    yield _FormInvalidChoice


def test_form_valid1(Form, pst, pst_tz):
    form = Form({"tz": pst})
    assert form.is_valid()
    assert form.cleaned_data["tz"] == pst_tz
    assert form.cleaned_data["tz_opt"] is None


def test_form_valid2(Form, gmt, gmt_tz, utc, utc_tz):
    form = Form({"tz": gmt, "tz_opt": utc})
    assert form.is_valid()
    assert form.cleaned_data["tz"] == gmt_tz
    assert form.cleaned_data["tz_opt"] == utc_tz


@pytest.mark.parametrize(
    "tz, tz_invalid_choice",
    [
        [lazy_fixture("invalid_tz"), None],
        [None, lazy_fixture("invalid_tz")],
    ],
)
def test_form_invalid(Form, tz, tz_invalid_choice):
    form = Form({"tz": tz, "tz_invalid_choice": tz_invalid_choice})
    assert not form.is_valid()


def test_form_uncommon(Form, uncommon_tz):
    form = Form({"tz": uncommon_tz})
    assert not form.is_valid()


def test_form_default_human_readable_choices_dont_have_underscores(Form):
    form = Form()
    for choice in form.fields["tz"].choices:
        assert "_" not in choice[1]


def test_form_invalid_choice_valid(FormInvalidChoice, pst, pst_tz):
    form = FormInvalidChoice({"tz": pst})
    assert form.is_valid()
    assert form.cleaned_data["tz"] == pst_tz


def test_form_invalid_chocie_invalid_choice(FormInvalidChoice, invalid_tz):
    form = FormInvalidChoice({"tz": invalid_tz})
    assert not form.is_valid()
