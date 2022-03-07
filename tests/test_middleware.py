import random

import pytest
import pytz
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest, HttpResponse
from django.utils.timezone import get_current_timezone

from timezone_field import TimeZoneField
from timezone_field.middleware import TimeZoneMiddleware


class User(AbstractUser):
    TIMEZONE_FIELD = "timezone"

    timezone = TimeZoneField()

    @classmethod
    def get_timezone_field_name(cls) -> str:
        return getattr(cls, "TIMEZONE_FIELD", "timezone")


@pytest.mark.django_db
def test_current_timezone():
    timezone = random.choice(pytz.all_timezones)
    middleware = TimeZoneMiddleware(lambda request: HttpResponse())
    user = User(username="test_user", email="test@example.com", timezone=timezone)
    user.set_password("test_password")
    user.save()
    request = HttpRequest()
    request.user = user
    response = middleware(request)
    assert isinstance(response, HttpResponse)
    assert timezone == str(get_current_timezone())
