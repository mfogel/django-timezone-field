from django import VERSION, conf


def use_pytz_default():
    return getattr(conf.settings, "USE_DEPRECATED_PYTZ", VERSION < (4, 0))
