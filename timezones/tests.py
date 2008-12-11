
__test__ = {"API_TESTS": r"""
>>> from datetime import datetime

>>> from django.conf import settings
>>> ORIGINAL_TIME_ZONE = settings.TIME_ZONE
>>> settings.TIME_ZONE = "UTC"

>>> from timezones import forms, decorators
>>> from timezones.utils import localtime_for_timezone, adjust_datetime_to_timezone

>>> localtime_for_timezone(datetime(2008, 6, 25, 18, 0, 0), "America/Denver").strftime("%m/%d/%Y %H:%I:%S")
'06/25/2008 12:12:00'

# the default case where no timezone is given explicitly. uses settings.TIME_ZONE.
>>> f = forms.LocalizedDateTimeField()
>>> f.clean("2008-05-30 14:30:00")
datetime.datetime(2008, 5, 30, 14, 30, tzinfo=<UTC>)

# specify a timezone explicity. this may come from a UserProfile for example.
>>> f = forms.LocalizedDateTimeField(timezone="America/Denver")
>>> f.clean("2008-05-30 14:30:00")
datetime.datetime(2008, 5, 30, 20, 30, tzinfo=<UTC>)

>>> f = forms.TimeZoneField()
>>> f.clean('US/Eastern')
<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>

>>> f = forms.TimeZoneField(required=False)
>>> f.clean('')
u''
>>> f.clean('US/Eastern')
<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>

>>> class Foo(object):
...     datetime = datetime(2008, 6, 20, 23, 58, 17)
...     @decorators.localdatetime('datetime')
...     def localdatetime(self):
...         return 'Australia/Lindeman'
...
>>> foo = Foo()
>>> foo.datetime
datetime.datetime(2008, 6, 20, 23, 58, 17)
>>> foo.localdatetime
datetime.datetime(2008, 6, 21, 9, 58, 17, tzinfo=<DstTzInfo 'Australia/Lindeman' EST+10:00:00 STD>)
>>> foo.localdatetime = datetime(2008, 6, 12, 23, 50, 0)
>>> foo.datetime
datetime.datetime(2008, 6, 12, 13, 50, tzinfo=<UTC>)
>>> foo.localdatetime
datetime.datetime(2008, 6, 12, 23, 50, tzinfo=<DstTzInfo 'Australia/Lindeman' EST+10:00:00 STD>)


>>> settings.TIME_ZONE = ORIGINAL_TIME_ZONE
"""}
