# modeled after django's versioning scheme, PEP 386
VERSION = (0, 3, 0, 'final', 0)

# adapted from django's get_version()
# see django.git/django/__init__.py
def get_version(version=VERSION):
    """Derives a PEP386-compliant version number from VERSION."""
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    main = '.'.join([str(x) for x in version[:3]])

    mapping = {
        'alpha': 'a',
        'beta': 'b',
        'rc': 'c',
    }
    sub = mapping[version[3]] + str(version[4]) if version[3] in mapping else ''

    return main + sub

__version__ = get_version()
