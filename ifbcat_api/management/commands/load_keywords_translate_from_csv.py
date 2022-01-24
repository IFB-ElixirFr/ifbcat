import csv
import logging
import os
from django.core.management import BaseCommand
from ifbcat_api.models import Keyword

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "file", type=str, default="import_data/keywords_english_translate.csv", help="Path to the CSV source file"
        )

    def handle(self, *args, **options):
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.DictReader(data_file, delimiter='\t')
            if not 'French_keywords' and 'English_keywords' in data.fieldnames:
                raise "The file is not conform!"
            else:
                count = 0
                uncount = 0
                for line in data:
                    for cle in Keyword.objects.all().order_by('keyword').values():
                        if line['English_keywords'] == cle['keyword']:
                            cle.keyword = str(line['English_keywords'])
                            cle.save()
                            count += 1

                print(str(count) + " Items have been updated")
                print(str(uncount) + " Items have not been updated")
