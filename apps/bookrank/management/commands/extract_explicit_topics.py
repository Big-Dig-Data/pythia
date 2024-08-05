"""
Extracts basic explicit topics:

* Author
* Publisher
* Language
* SubjectCategory PSH

from Works and create the connections between works and topics
"""

import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from core.models import SingletonValue
from core.logic.updates import get_last_date, update_last_date
from ...logic.command_help import get_workset_by_name_or_command_error
from ...logic.topics import (
    marc_author_topics,
    marc_publisher_topics,
    extract_m2m_explicit_topics_from_works,
    marc_psh_topics_simple,
    extract_fk_explicit_topics_from_works,
    marc_owner_institution_topics,
    marc_topics_by_type,
)
from ...logic import topics

from ...models import (
    Author,
    Publisher,
    SubjectCategory,
    AuthorWork,
    PublisherWork,
    SubjectCategoryWork,
    OwnerInstitution,
    WorkCategory,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    singleton_prefix = 'last_update'

    def add_arguments(self, parser):
        parser.add_argument('work_set', type=str, help="Name or UUID of the WorkSet to use.")
        parser.add_argument(
            '-l',
            '--limit',
            type=str,
            dest='limit',
            default='',
            choices=[
                'author',
                'psh',
                'lang',
                'publisher',
                'owner_institution',
                'category',
                'czenas',
            ],
            help="Only run for the selected topic type.",
        )
        parser.add_argument(
            '-a',
            '--all',
            dest='ignore_last_update',
            action='store_true',
            help="Ignore last_update detection and process all works.",
        )

    def handle(self, *args, **options):
        workset = get_workset_by_name_or_command_error(options['work_set'], self)
        logger.info('Working with workset: %s', workset)
        logger.info('Extracting foreign-key based topics')
        work_category_extractor = getattr(topics, settings.WORK_CATEGORY_EXTRACTOR)
        logger.debug('Using work category extractor: %s', work_category_extractor)
        for name, extractor, model_cls in (
            ('owner_institution', marc_owner_institution_topics, OwnerInstitution),
            ('category', work_category_extractor, WorkCategory),
        ):
            if options['limit'] in ('', name):
                logger.info('Starting extraction of "%s"', name)
                last_update = (
                    get_last_date(name, logger) if not options['ignore_last_update'] else None
                )
                with transaction.atomic():
                    stats = extract_fk_explicit_topics_from_works(
                        workset, extractor, model_cls, name, newer_than=last_update
                    )
                logger.info("Sync stats: %s", stats)
                update_last_date(name)

        logger.info('Extracting many-to-many based topics')
        # prepare PSH
        psh_root, created = SubjectCategory.objects.get_or_create(
            uid='PSH-ROOT', parent=None, work_set=workset, defaults={'name': 'PSH'}
        )
        if created:
            logger.info('Created subject category tree root for PSH')
        psh_topic_filter = {'tree_id': psh_root.tree_id}
        # prepare czenas tree
        czenas_root, created = SubjectCategory.objects.get_or_create(
            uid='CZENAS-ROOT', parent=None, work_set=workset, defaults={'name': 'CZENAS'}
        )
        if created:
            logger.info('Created subject category tree root for CZENAS')
        czenas_topic_filter = {'tree_id': czenas_root.tree_id}
        marc_czenas_extractor = lambda work: marc_topics_by_type(work, 'czenas')
        # topics with function based extractors
        for (
            name,
            extractor,
            model_cls,
            connector_cls,
            id_attr,
            topic_filter,
            topic_extra_attrs,
            cont_dict,
        ) in (
            ('author', marc_author_topics, Author, AuthorWork, 'name', {}, None, False),
            ('publisher', marc_publisher_topics, Publisher, PublisherWork, 'name', {}, None, False),
            (
                'psh',
                marc_psh_topics_simple,
                SubjectCategory,
                SubjectCategoryWork,
                'uid',
                psh_topic_filter,
                None,
                True,
            ),
            (
                'czenas',
                marc_czenas_extractor,
                SubjectCategory,
                SubjectCategoryWork,
                'uid',
                czenas_topic_filter,
                {'parent': czenas_root},
                False,
            ),
        ):
            if options['limit'] in ('', name):
                logger.info('Starting extraction of "%s"', name)
                last_update = (
                    get_last_date(name, logger) if not options['ignore_last_update'] else None
                )
                with transaction.atomic():
                    stats = extract_m2m_explicit_topics_from_works(
                        workset,
                        extractor,
                        model_cls,
                        connector_cls,
                        id_attr=id_attr,
                        topic_filter=topic_filter,
                        topic_extra_attrs=topic_extra_attrs,
                        newer_than=last_update,
                        controlled_dictionary=cont_dict,
                    )
                logger.info("Sync stats: %s", stats)
                update_last_date(name)
