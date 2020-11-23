import os

from django.core.management import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    import_data = "./import_data"

    def import_catalog(self):
        call_command(
            'load_persons',
            os.path.join(self.import_data, "persons.csv"),
            os.path.join(self.import_data, "drupal_db_dump", "users.txt"),
        )
        call_command('load_bioinformatics_teams', os.path.join(self.import_data, "platforms.csv"))
        call_command('load_expertises', os.path.join(self.import_data, "expertises.csv"))
        call_command('load_databases', os.path.join(self.import_data, "databases.csv"))
        call_command('load_tools', os.path.join(self.import_data, "tools.csv"))
        # call_command('load_services')
        call_command('load_training', os.path.join(self.import_data, "training.csv"))
        # call_command('load_training_material')
        call_command('load_events', os.path.join(self.import_data, "events.csv"))
        # call_command('load_infrastructure')

        # load_biotools works but the call should be avoided here
        # to avoid spamming NCBI for queries each time we run tests.
        # call_command('load_biotools')

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_catalog()
