from django.core.management import BaseCommand
from django.core.management import call_command

from catalogue.settings import BASE_DIR


class Command(BaseCommand):
    def import_catalog(self):
        call_command('load_platforms')
        call_command('load_databases')
        # call_command('load_tools')
        call_command('load_services')
        call_command('load_expertises')
        call_command('load_persons')
        call_command('load_training')
        call_command('load_training_material')
        call_command('load_events')
        call_command('load_infrastructure')

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_catalog()
