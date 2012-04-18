=======================
 django-timezone-field
=======================

A Django app providing database store for `pytz`__ timezone objects.

Example
=======
::

    from django.db import models
    from timezone_field.fields import TimeZoneField

    class MyClass(models.Model):
        timezone = TimeZoneField()

    my_inst = MyClass(timezone='America/Los_Angeles')
    my_inst.full_clean()
    my_inst.save()

    tz = my_inst.timezone
    str(tz)     # 'America/Los_Angeles'
    repr(tz)    # "<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>"

Documentation
=============

For details, see the docstring on timezone_field.fields.TimeZoneField.

Found a Bug?
============

To file a bug or submit a patch, please head over to the `django-timezone-field repository`__.

Credits
=======

Originally adapted from `Brian Rosner's django-timezones`__.


__ http://pypi.python.org/pypi/pytz
__ https://github.com/mfogel/django-timezone-field/
__ https://github.com/brosner/django-timezones/
