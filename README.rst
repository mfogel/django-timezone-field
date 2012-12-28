django-timezone-field
=====================

.. image:: https://api.travis-ci.org/mfogel/django-timezone-field.png?branch=develop
   :alt: Build Status
   :target: https://travis-ci.org/mfogel/django-timezone-field

A Django app providing database and form fields for `pytz`__ timezone objects.

Examples
--------

Database Field
~~~~~~~~~~~~~~

.. code:: python

    import pytz
    from django.db import models
    from timezone_field import TimeZoneField

    class MyModel(models.Model):
        timezone1 = TimeZoneField()
        timezone2 = TimeZoneField()
        timezone3 = TimeZoneField()

    my_inst = MyModel(
        timezone1='America/Los_Angeles',    # assignment of a string
        timezone2=pytz.timezone('Turkey'),  # assignment of a pytz.DstTzInfo
        timezone3=pytz.UTC,                 # assignment of pytz.UTC singleton
    )
    my_inst.full_clean()  # validates against pytz.all_timezones
    my_inst.save()        # values stored in DB as strings

    tz = my_inst.timezone1  # values retrieved as pytz objects
    repr(tz)                # "<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>"


Form Field
~~~~~~~~~~

.. code:: python

    from django import forms
    from timezone_field import TimeZoneFormField

    class MyForm(forms.Form):
        timezone = TimeZoneFormField()

    my_form = MyForm({
        'timezone': 'America/Los_Angeles',
    })
    my_form.full_clean()  # validates against pytz.all_timezones

    tz = my_form.cleaned_data['timezone']  # values retrieved as pytz objects
    repr(tz)                               # "<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>"


Installation
------------

Now on `pypi`__!

.. code:: sh

    pip install django-timezone-field

Running the Tests
-----------------

Using `Doug Hellman's virtualenvwrapper`__:

.. code:: sh

    mktmpenv
    pip install django-timezone-field
    export DJANGO_SETTINGS_MODULE=timezone_field.test_settings
    django-admin.py test timezone_field

Found a Bug?
------------

To file a bug or submit a patch, please head over to `django-timezone-field on github`__.

Credits
-------

Originally adapted from `Brian Rosner's django-timezones`__.


__ http://pypi.python.org/pypi/pytz/
__ http://pypi.python.org/pypi/django-timezone-field/
__ http://www.doughellmann.com/projects/virtualenvwrapper/
__ https://github.com/mfogel/django-timezone-field/
__ https://github.com/brosner/django-timezones/
