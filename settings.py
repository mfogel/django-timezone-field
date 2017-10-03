import os

from django.conf import settings


def configure_settings():
    """
    Configures settings for manage.py and for run_tests.py.
    """
    if not settings.configured:
        # Determine the database settings depending on if a test_db var is set in CI mode or not
        test_db = os.environ.get('DB', None)
        if test_db is None:
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'ambition_test',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'db'
            }
        elif test_db == 'postgres':
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'USER': 'postgres',
                'NAME': 'django_timezone_field',
            }
        elif test_db == 'sqlite':
            db_config = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'django_timezone_field',
            }
        else:
            raise RuntimeError('Unsupported test DB {0}'.format(test_db))

        settings.configure(
            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
            NOSE_ARGS=['--nocapture', '--nologcapture', '--verbosity=1'],
            MIDDLEWARE_CLASSES=(),
            DATABASES={
                'default': db_config,
            },
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.admin',
                'timezone_field',
                'timezone_field.tests',
            ),
            ROOT_URLCONF='timezone_field.urls',
            DEBUG=False,
        )
