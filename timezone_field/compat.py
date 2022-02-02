try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # pylint: disable=unused-import
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # noqa: F401
