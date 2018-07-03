import logging
import sys

from app.admin import create_app

logging.basicConfig(stream=sys.stderr)

app = create_app()
