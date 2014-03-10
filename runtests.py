#!/usr/bin/env python

import os
import sys

from django.conf import settings


def runtests():

    test_args = ['timezone_field']
    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'timezone_field.test_settings'

    import timezone_field.test_settings  # Fixes Django 1.4 bug
    from django.test.simple import DjangoTestSuiteRunner
    failures = DjangoTestSuiteRunner(failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
