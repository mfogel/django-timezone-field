from datetime import tzinfo
from typing import Callable, Optional

from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.functional import SimpleLazyObject


class TimezoneMiddleware:
    """
    Set timezone for the current thread from the value in user instance.
    """

    def __init__(self, get_response: Callable[..., HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        assert hasattr(request, "user"), (
            f"`{self.__class__.__name__}` requires `AuthenticationMiddleware` "
            "Edit your MIDDLEWARE setting to insert "
            "`django.contrib.auth.middleware.AuthenticationMiddleware` before "
            f"`{self.__class__.__name__}`."
        )

        assert hasattr(request.user.__class__, "get_timezone_field_name"), (
            f"`{request.user.__class.__name__}` must implement "
            "`get_timezone_field_name()` classmethod."
        )

        timezone_field_name: str = request.user.__class__.get_timezone_field_name()  # type: ignore

        timezone: Optional[tzinfo] = getattr(
            request.user, timezone_field_name, None
        )

        if isinstance(timezone, (tzinfo, str)):
            timezone.activate(time_zone)
        else:
            timezone.deactivate()

        return self.get_response(request)
