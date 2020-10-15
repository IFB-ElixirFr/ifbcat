import os

from django.core.management import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    import_data = "./import_data"

    def import_catalog(self):
        call_command('load_persons', os.path.join(self.import_data, "persons.csv"))
        call_command('load_bioinformatics_teams', os.path.join(self.import_data, "platforms.csv"))
        call_command('load_expertises', os.path.join(self.import_data, "expertises.csv"))
        # call_command('load_databases')
        # # call_command('load_tools')
        # call_command('load_services')
        # call_command('load_training')
        # call_command('load_training_material')
        # call_command('load_events')
        # call_command('load_infrastructure')

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_catalog()
