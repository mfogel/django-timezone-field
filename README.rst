django-timezone-field
=====================

.. image:: https://secure.travis-ci.org/mfogel/django-timezone-field.png
   :alt: Build Status
   :target: https://secure.travis-ci.org/mfogel/django-timezone-field

A Django app providing database store for `pytz`__ timezone objects.

Example
-------
.. code:: python

    import pytz
    from django.db import models
    from timezone_field import TimeZoneField

    class MyModel(models.Model):
        timezone1 = TimeZoneField()
        timezone2 = TimeZoneField()
        timezone3 = TimeZoneField()

    my_inst = MyModel(
        timezone1='America/Los_Angeles',   # assignment of a string
        timezone2=pytz.timezone('Turkey'), # assignment of a pytz.DstTzInfo
        timezone3=pytz.UTC,                # assignment of pytz.UTC singleton
    )
    my_inst.full_clean()
    my_inst.save() # values stored in DB as strings

    tz = my_inst.timezone1
    repr(tz)    # "<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>"

Documentation
-------------

For details, see the docstring on timezone_field.fields.TimeZoneField.

Found a Bug?
------------

To file a bug or submit a patch, please head over to `django-timezone-field on github`__.

Credits
-------

Originally adapted from `Brian Rosner's django-timezones`__.


__ http://pypi.python.org/pypi/pytz
__ https://github.com/mfogel/django-timezone-field/
__ https://github.com/brosner/django-timezones/
