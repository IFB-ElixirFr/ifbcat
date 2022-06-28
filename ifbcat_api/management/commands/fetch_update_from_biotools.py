import logging

from django.core.management import BaseCommand

from ifbcat_api.tasks import update_tools

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_tools()
