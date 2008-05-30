
__test__ = {"API_TESTS": r"""
>>> from django.conf import settings
>>> ORIGINAL_TIME_ZONE = settings.TIME_ZONE
>>> settings.TIME_ZONE = "UTC"

>>> from timezones import forms

>>> f = forms.LocalizedDateTimeField("America/Denver")
>>> f.clean("2008-05-30 14:30:00")
datetime.datetime(2008, 5, 30, 20, 30, tzinfo=<UTC>)

>>> settings.TIME_ZONE = ORIGINAL_TIME_ZONE
"""}
