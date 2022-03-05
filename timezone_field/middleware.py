from datetime import tzinfo
from typing import Callable, Optional, Union

from django.http import HttpRequest, HttpResponse
from django.utils import timezone


class TimeZoneMiddleware:
    """
    Set timezone for the current thread from the value in user instance.
    """

    user_property_not_defined = (
        "`TimeZoneMiddleware` requires `AuthenticationMiddleware` "
        "Edit your MIDDLEWARE setting to insert "
        "`django.contrib.auth.middleware.AuthenticationMiddleware` before "
        "`TimeZoneMiddleware`."
    )
    classmethod_not_implemented = "`get_timezone_field_name()` classmethod not implemented."

    def __init__(self, get_response: Callable[..., HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        assert hasattr(request, "user"), self.user_property_not_defined
        assert hasattr(request.user.__class__, "get_timezone_field_name"), self.classmethod_not_implemented
        timezone_field_name: str = request.user.__class__.get_timezone_field_name()  # type: ignore
        timezone_value: Optional[Union[tzinfo, str]] = getattr(request.user, timezone_field_name, None)
        if isinstance(timezone_value, (tzinfo, str)):
            timezone.activate(timezone_value)
        else:
            timezone.deactivate()
        return self.get_response(request)
