import json
import logging
import os

from django.core.management import BaseCommand

from ifbcat_api import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--cache_dir',
            help='Folder where are/will be stored the raw json downloaded',
            type=str,
        )

    def handle(self, cache_dir, *args, **options):
        for filename, klass, identifying_fields in [
            ("Topic.json", models.Topic, {"uri"}),
        ]:
            with open(os.path.join(cache_dir, filename)) as f:
                for item in json.load(f):
                    sub_item = dict((k, v) for k, v in item.items() if k in identifying_fields)
                    to_defaults = dict((k, v) for k, v in item.items() if k not in identifying_fields)
                    klass.objects.update_or_create(**sub_item, defaults=to_defaults)
