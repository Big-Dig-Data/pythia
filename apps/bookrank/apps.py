import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class BookrankConfig(AppConfig):
    name = 'bookrank'
