#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "timezones",
    version = "0.1.0-pre",
    author = "Brian Rosner",
    author_email = "brosner@gmail.com",
    url = "http://code.google.com/p/django-timezones/",
    license = "BSD",
    packages = [
        "timezones",
        "timezones.templatetags",
    ],
    package_dir = {"timezones": "timezones"},
    install_requires = [
        "pytz>=2008i",
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Framework :: Django",
    ]
)