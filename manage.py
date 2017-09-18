#!/usr/bin/env  python
import os  # PYTHONWARNINGS=ignore
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tms.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
