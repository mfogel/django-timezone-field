import pytest
from pytest_lazyfixture import lazy_fixture


@pytest.mark.django_db
def test_valid_with_defaults(Model, ModelForm, pst_tz, gmt, gmt_tz):
    # seems there should be a better way to get a form's default values...?
    # http://stackoverflow.com/questions/7399490/
    data = dict((field_name, field.initial) for field_name, field in ModelForm().fields.items())
    data.update({"tz": gmt})
    form = ModelForm(data=data)
    assert form.is_valid()
    form.save()
    assert Model.objects.count() == 1

    m = Model.objects.get()
    assert m.tz == gmt_tz
    assert m.tz_opt is None
    assert m.tz_opt_default == pst_tz
    assert m.tz_gmt_offset is None


@pytest.mark.django_db
def test_valid_specify_all(Model, ModelForm, utc, pst, gmt, utc_tz, gmt_tz, pst_tz):
    form = ModelForm(
        {
            "tz": utc,
            "tz_opt": pst,
            "tz_opt_default": gmt,
            "tz_gmt_offset": utc,
        }
    )
    assert form.is_valid()
    form.save()
    assert Model.objects.count() == 1

    m = Model.objects.get()
    assert m.tz == utc_tz
    assert m.tz_opt == pst_tz
    assert m.tz_opt_default == gmt_tz
    assert m.tz_gmt_offset == utc_tz


@pytest.mark.parametrize(
    "tz, error_keyword",
    [
        [None, "required"],
        [lazy_fixture("invalid_tz"), "choice"],
        [lazy_fixture("uncommon_tz"), "choice"],
    ],
)
def test_invalid_not_blank(ModelForm, tz, error_keyword):
    form = ModelForm({"tz": tz})
    assert not form.is_valid()
    assert any(error_keyword in e for e in form.errors["tz"])


def test_default_human_readable_choices_dont_have_underscores(ModelForm, pst_tz):
    form = ModelForm()
    pst_choice = [c for c in form.fields["tz"].choices if c[0] == pst_tz]
    assert pst_choice[0][1] == "America/Los Angeles"


def test_display_gmt_offsets(ModelForm, use_pytz, pst_tz):
    if not use_pytz:
        # The zoneinfo implementation does not support the
        # deprecated display_GMT_offset parameter.
        return
    form = ModelForm({'tz_gmt_offset': pst_tz})
    c = [c for c in form.fields['tz_gmt_offset'].choices if c[0] == pst_tz]
    assert c[0][1] == 'GMT-08:00 America/Los Angeles'
