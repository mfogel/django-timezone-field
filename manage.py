#!/usr/bin/env python
import sys

from settings import configure_settings


if __name__ == '__main__':
    configure_settings()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
