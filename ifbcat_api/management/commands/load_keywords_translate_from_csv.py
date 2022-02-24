import csv
import json
import logging
from tqdm import tqdm
import os
from django.core.management import BaseCommand
from ifbcat_api.models import Keyword

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="import_data/keywords_english_translate_testok_.csv",
            help="Path to the CSV source file",
        )

    def handle(self, *args, **options):
        if not os.path.exists(options["file"]):
            logger.error(f"Cannot find the file named {options['file'][12:]}")
            return

        file_dict = {}
        count = 0
        untranslated_nb = 0
        with open(options["file"], encoding='utf-8') as data_file:
            data = csv.reader(data_file, delimiter='\t')
            data_file.seek(0)
            next(data)  # skip first line as there is always a header we guests

            for data_object in data:
                file_dict[data_object[0]] = data_object[1]

            qs_keyword = Keyword.objects.all().order_by('keyword')
            for key in qs_keyword:
                str_key = key.keyword.strip()
                if file_dict.get(str_key) == "To_translate":
                    pass
                elif str_key in file_dict.keys() and str_key not in file_dict.values():
                    key.keyword = file_dict.get(str_key)
                    key.save()
                    count += 1
                elif str_key in file_dict.values():
                    logger.info(f"{str_key} has already been translated!")
                else:
                    print(untranslated_nb, str_key)
                    print("___________")
                    file_dict[str_key] = "To_translate"
                    untranslated_nb += 1

            # f = open(options["file"], 'r+')
            # f.truncate(0)
            with open(os.path.join(options["file"]), 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['French_keywords', 'English_keywords'], delimiter='\t')
                writer.writeheader()
                for key, value in file_dict.items():
                    writer.writerow({'French_keywords': key, 'English_keywords': value})

            logger.info(f"{count} Items have been updated")
            logger.info(f"{untranslated_nb} Items have been added to the csv file {options['file']}")
