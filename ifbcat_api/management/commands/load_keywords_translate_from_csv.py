import csv
import logging
import os
from django.core.management import BaseCommand
from ifbcat_api.models import Keyword

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file", type=str, default="import_data/keywords_english_translate.csv", help="Path to the CSV source file"
        )

    def handle(self, *args, **options):
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.DictReader(data_file, delimiter='\t')
            if not 'French_keywords' and 'English_keywords' in data.fieldnames:
                raise "The file is not conform!"
            else:
                count = 0
                uncounted = 0
                untranslated = []
                for line in data:
                    for cle in Keyword.objects.filter(keyword=line['French_keywords']):
                        if cle.keyword != line['French_keywords']:
                            print(uncounted, cle.keyword)
                            uncounted += 1
                            untranslated.append(cle.keyword)
                            print("non")

                        else:
                            cle.keyword = line['English_keywords']
                            cle.save()
                            count += 1
                with open("import_data/keywords_english_translate.csv", 'a') as f_object:
                    writer_object = csv.writer(f_object)
                    print(untranslated)
                    for keyword in untranslated:
                        writer_object.writerow(keyword)
                    f_object.close()
                print(str(count) + " Items have been updated")
                print(str(uncounted) + " Items have been added to the csvfile")
