import random

import pytz
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from django.utils.timezone import get_current_timezone

from timezone_field import TimeZoneField
from timezone_field.middleware import TimeZoneMiddleware


class User(AbstractUser):
    TIMEZONE_FIELD = "timezone"

    timezone = TimeZoneField()

    @classmethod
    def get_timezone_field_name(cls) -> str:
        return getattr(cls, "TIMEZONE_FIELD", "timezone")


class TimeZoneMiddlewareTest(TestCase):
    middleware = TimeZoneMiddleware(lambda request: HttpResponse())
    timezone = random.choice(pytz.all_timezones)

    def setUp(self):
        user = User(username="test_user", email="test@example.com", timezone=self.timezone)
        user.set_password("test_password")
        user.save()
        request = HttpRequest()
        request.user = user
        self.user = user
        self.request = request

    def test_current_timezone(self):
        response = self.middleware(self.request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(self.timezone, str(get_current_timezone()))
