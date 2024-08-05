"""
Invalidates all tables with Cachalot - useful if Cachalot was disabled for some commands
and the case get out of whack
"""

import logging

from cachalot.api import invalidate
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        invalidate()
        logger.info('Done invalidating cachalot cache')
