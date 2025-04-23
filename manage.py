#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from datetime import datetime
# setup basuc logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_run_time():
    """Log the run time of the script."""
    start_time = datetime.now()
    logger.info(f"Script started at {start_time}")

    # Your script logic here

    end_time = datetime.now()
    logger.info(f"Script ended at {end_time}")
    logger.info(f"Total run time: {end_time - start_time}")


def main():
    """Run administrative tasks."""
    log_run_time()  # Log the run time of the script
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
