import pytest
from django.core.exceptions import ValidationError
from pytest_lazy_fixtures import lf as lazy_fixture

from timezone_field import TimeZoneField

pytestmark = pytest.mark.filterwarnings("ignore:Model 'tests._model.*' was already registered.")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "input_tz, output_tz",
    [
        [lazy_fixture("pst"), lazy_fixture("pst_tz")],
        [lazy_fixture("pst_tz"), lazy_fixture("pst_tz")],
        [lazy_fixture("gmt"), lazy_fixture("gmt_tz")],
        [lazy_fixture("gmt_tz"), lazy_fixture("gmt_tz")],
        [lazy_fixture("utc"), lazy_fixture("utc_tz")],
        [lazy_fixture("utc_tz"), lazy_fixture("utc_tz")],
    ],
)
def test_valid_dst_tz(Model, input_tz, output_tz):
    m = Model.objects.create(tz=input_tz, tz_opt=input_tz, tz_opt_default=input_tz)
    m.full_clean()
    m = Model.objects.get(pk=m.pk)
    assert m.tz == output_tz
    assert m.tz_opt == output_tz
    assert m.tz_opt_default == output_tz


@pytest.mark.django_db
def test_valid_default_values(Model, utc_tz, pst_tz):
    m = Model.objects.create(tz=utc_tz)
    m.full_clean()
    m = Model.objects.get(pk=m.pk)
    assert m.tz_opt is None
    assert m.tz_opt_default == pst_tz


def test_valid_default_values_without_saving_to_db(Model, utc_tz, pst_tz):
    m = Model(tz=utc_tz)
    m.full_clean()
    assert m.tz_opt is None
    assert m.tz_opt_default == pst_tz


@pytest.mark.django_db
@pytest.mark.parametrize("tz_opt", ["", None])
def test_valid_blank(Model, pst, tz_opt):
    m = Model.objects.create(tz=pst, tz_opt=tz_opt)
    m.full_clean()
    m = Model.objects.get(pk=m.pk)
    assert m.tz_opt is None


@pytest.mark.django_db
@pytest.mark.parametrize("filter_tz", [lazy_fixture("pst"), lazy_fixture("pst_tz")])
def test_string_value_lookup(Model, pst, filter_tz):
    Model.objects.create(tz=pst)
    qs = Model.objects.filter(tz=filter_tz)
    assert qs.count() == 1


@pytest.mark.parametrize(
    "input_tz, output_tz",
    [
        [lazy_fixture("pst"), lazy_fixture("pst_tz")],
        [lazy_fixture("pst_tz"), lazy_fixture("pst_tz")],
        ["", None],
        [None, None],
    ],
)
def test_string_value_assignment_without_save(Model, utc, input_tz, output_tz):
    m = Model(tz=utc, tz_opt=utc)
    m.tz_opt = input_tz
    assert m.tz_opt == output_tz


@pytest.mark.parametrize("tz", [None, "", "not-a-tz", 4, object()])
def test_invalid_input(Model, tz):
    with pytest.raises(ValidationError):
        # Most invalid values are detected at creation/assignment.
        # Invalid blank values aren't detected until clean/save.
        m = Model(tz=tz)
        if tz is None or tz == "":
            assert m.tz is None
            m.full_clean()


def test_three_positional_args_does_not_throw():
    TimeZoneField("a verbose name", "a name", True)


def test_four_positional_args_throws():
    with pytest.raises(ValueError):
        TimeZoneField("a verbose name", "a name", True, 42)


def test_default_human_readable_choices_dont_have_underscores(Model, pst_tz):
    m = Model(tz=pst_tz)
    assert m.get_tz_display() == "America/Los Angeles"


@pytest.mark.django_db
def test_with_limited_choices_valid_choice(ModelChoice, pst, pst_tz):
    ModelChoice.objects.create(tz_superset=pst, tz_subset=pst)
    m = ModelChoice.objects.get()
    assert m.tz_superset == pst_tz
    assert m.tz_subset == pst_tz


@pytest.mark.parametrize("kwargs", [{"tz_superset": "not a tz"}, {"tz_subset": "Europe/Brussels"}])
def test_with_limited_choices_invalid_choice(ModelChoice, kwargs):
    with pytest.raises(ValidationError):
        m = ModelChoice(**kwargs)
        m.full_clean()


@pytest.mark.django_db
def test_with_limited_choices_old_format_valid_choice(ModelOldChoiceFormat, pst, pst_tz):
    ModelOldChoiceFormat.objects.create(tz_superset=pst, tz_subset=pst)
    m = ModelOldChoiceFormat.objects.get()
    assert m.tz_superset == pst_tz
    assert m.tz_subset == pst_tz


@pytest.mark.parametrize("kwargs", [{"tz_superset": "not a tz"}, {"tz_subset": "Europe/Brussels"}])
def test_with_limited_choices_old_format_invalid_choice(ModelOldChoiceFormat, kwargs):
    with pytest.raises(ValidationError):
        m = ModelOldChoiceFormat(**kwargs)
        m.full_clean()
