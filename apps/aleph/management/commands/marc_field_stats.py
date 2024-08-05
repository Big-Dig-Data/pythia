"""
Read OAI files from Aleph and import them into the database
"""

import logging
from collections import Counter
from pathlib import Path

from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.db.transaction import atomic, set_autocommit, commit

from ...logic.data_import import import_aleph_marc_xml, filename_to_uid
from ...models import AlephEntry

logger = logging.getLogger(__name__)


class Node(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 1

    def increase(self):
        self.counter += 1


class Command(BaseCommand):

    help = 'Print out stats of MARC fields usage'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.value_stats = False
        self.top = 0

    def add_arguments(self, parser):
        parser.add_argument('-l', '--value-stats', action='store_true', dest='value_stats')
        parser.add_argument('-t', '--top', type=int, default=0, dest='top')

    def sync_entry_with_tree(self, entry, tree):
        if type(entry) is dict:
            for key, value in entry.items():
                subtree = tree.get(key)
                if subtree is not None:
                    subtree.increase()
                else:
                    subtree = Node()
                    tree[key] = subtree
                self.sync_entry_with_tree(value, subtree)
        elif type(entry) is list:
            for value in entry:
                self.sync_entry_with_tree(value, tree)
        else:
            if self.value_stats:
                # we process this only optionally
                subtree = tree.get(entry)
                if subtree is not None:
                    subtree.increase()
                else:
                    subtree = Node()
                    tree[entry] = subtree

    def print_tree(self, tree, level=0):
        for i, (key, value) in enumerate(sorted(tree.items(), key=lambda x: -x[1].counter)):
            print(2 * level * " " + "-", key, value.counter)
            self.print_tree(value, level=level + 1)
            if self.top and i + 1 >= self.top:
                break

    def handle(self, *args, **options):
        self.value_stats = options['value_stats']
        self.top = options['top']
        tree = Node()
        for entry in AlephEntry.objects.all():
            self.sync_entry_with_tree(entry.raw_data, tree)
        self.print_tree(tree)
