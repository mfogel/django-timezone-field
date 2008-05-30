
__test__ = {"API_TESTS": r"""
>>> from django.conf import settings
>>> ORIGINAL_TIME_ZONE = settings.TIME_ZONE
>>> settings.TIME_ZONE = "UTC"

>>> from timezones import forms

# the default case where no timezone is given explicitly.
# uses settings.TIME_ZONE.
>>> f = forms.LocalizedDateTimeField()
>>> f.clean("2008-05-30 14:30:00")
datetime.datetime(2008, 5, 30, 14, 30, tzinfo=<UTC>)

# specify a timezone explicity. this may come from a UserProfile for example.
>>> f = forms.LocalizedDateTimeField(timezone="America/Denver")
>>> f.clean("2008-05-30 14:30:00")
datetime.datetime(2008, 5, 30, 20, 30, tzinfo=<UTC>)

>>> settings.TIME_ZONE = ORIGINAL_TIME_ZONE
"""}
