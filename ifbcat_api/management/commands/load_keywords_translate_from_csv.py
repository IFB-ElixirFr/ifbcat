import csv
import json
import logging
import os
from django.core.management import BaseCommand
from ifbcat_api.models import Keyword

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="import_data/keywords_english_translate1.csv",
            help="Path to the CSV source file",
        )

    def handle(self, *args, **options):
        if not os.path.exists(options["file"]):
            logger.error(f"Cannot find the file named {options['file'][12:]}")
            with open(os.path.join(options["file"]), 'a+', encoding='utf-8', newline='') as data_file:
                data = csv.DictWriter(data_file, delimiter='\t', fieldnames=['French_keywords', 'English_keywords'])
                data.writeheader()

                qs_dict = Keyword.objects.all().values().order_by('keyword')
                data.writerows({'French_keywords': row['keyword'], 'English_keywords': 'Something'} for row in qs_dict)
                logger.info(f"{len(qs_dict)} have been added to the new file named {options['file'][12:]}")

        with open(os.path.join(options["file"]), encoding='utf-8', newline='') as data_file:
            data = csv.DictReader(data_file, delimiter='\t')
            if ['French_keywords', 'English_keywords'] == data.fieldnames:
                count = 0
                untranslated = 0
                qs_dict = Keyword.objects.all().values().order_by('keyword')
                file_dict = list(data)

                dict_to_list_qs = [item_qs['keyword'] for item_qs in qs_dict]
                dict_to_list_file = [line_file['French_keywords'] for line_file in file_dict]
                diff_list = list(set(dict_to_list_qs) - set(dict_to_list_file))
                untranslated_fr = [[line, ''] for line in diff_list]

                for line in data:
                    for cle in Keyword.objects.filter(keyword__iexact=line['French_keywords']):
                        cle.keyword = line['English_keywords']
                        cle.save()
                        count += 1
                with open("import_data/keywords_english_translate.csv", 'a', newline='') as f_object:
                    writer_object = csv.writer(f_object)
                    for line in untranslated_fr:
                        writer_object.writerow(line)
                        untranslated += 1
                    f_object.close()
                logger.info(f"{count} Items have been updated")
                logger.info(f"{untranslated} Items have been added to the csv file")
