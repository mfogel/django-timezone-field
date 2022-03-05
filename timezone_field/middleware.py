from datetime import tzinfo
from typing import Callable, Optional, Union

from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.functional import SimpleLazyObject


class TimeZoneMiddleware:
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
        assert hasattr(
            request.user.__class__, "get_timezone_field_name"
        ), "`get_timezone_field_name()` classmethod not implemented."
        timezone_field_name: str = request.user.__class__.get_timezone_field_name()  # type: ignore
        timezone_value: Optional[Union[tzinfo, str]] = getattr(request.user, timezone_field_name, None)
        if isinstance(timezone_value, (tzinfo, str)):
            timezone.activate(timezone_value)
        else:
            timezone.deactivate()
        return self.get_response(request)
