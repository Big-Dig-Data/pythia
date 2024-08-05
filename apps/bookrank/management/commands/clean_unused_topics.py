"""
Finds topics that are not used and deletes them
"""

import logging
from collections import Counter

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from ...logic.command_help import get_workset_by_name_or_command_error
from ...logic.cleanup import clean_all_unused_topics

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Finds topics that are not used and deletes them'

    def add_arguments(self, parser):
        parser.add_argument('work_set', type=str, help="Name or UUID of the WorkSet to use.")

    @atomic
    def handle(self, *args, **options):
        workset = get_workset_by_name_or_command_error(options['work_set'], self)
        logger.info('Working with workset: %s', workset)
        stats = clean_all_unused_topics(workset)
        logger.info("Stats: %s", stats)
