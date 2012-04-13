from setuptools import setup

setup(
    name = 'django-timezone-field',
    version = __import__('timezone_field').__version__,
    author = 'Mike Fogel',
    author_email = 'mike@fogel.ca',
    description = 'A Django reusable app to save timezones to a database',
    long_description = open('README').read(),
    url = 'http://github.com/mfogel/django-timezone-field/',
    license = 'BSD',
    packages = [
        'timezone_field',
    ],
    install_requires = ['django', 'pytz'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Framework :: Django',
    ]
)
