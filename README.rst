django-timezone-field
=====================

.. image:: https://secure.travis-ci.org/mfogel/django-timezone-field.png
   :alt: Build Status
   :target: https://secure.travis-ci.org/mfogel/django-timezone-field

A Django app providing database store for `pytz`__ timezone objects.

Example
-------
::

    from django.db import models
    from timezone_field.fields import TimeZoneField

    class MyModel(models.Model):
        timezone = TimeZoneField()

    # valid assignment values include:
    #   * any string that validates against pytz.all_timezones
    #   * any instance of pytz.tzinfo.DstTzInfo or pytz.tzinfo.StaticTzInfo
    #   * the pytz.UTC singleton
    my_inst = MyModel(timezone='America/Los_Angeles')
    my_inst.full_clean()

    # under the hood, values are stored in the database as strings
    my_inst.save()

    # values read from the field are either instances of pytz.tzinfo.DstTzinfo
    # or pytz.tzinfo.StaticTzInfo, or the pytz.UTC singleton
    tz = my_inst.timezone
    repr(tz)    # "<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>"

Documentation
-------------

For details, see the docstring on timezone_field.fields.TimeZoneField.

Found a Bug?
------------

To file a bug or submit a patch, please head over to the `django-timezone-field repository`__.

Credits
-------

Originally adapted from `Brian Rosner's django-timezones`__.


__ http://pypi.python.org/pypi/pytz
__ https://github.com/mfogel/django-timezone-field/
__ https://github.com/brosner/django-timezones/
