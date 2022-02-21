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
            default="import_data/keywords_english_translate23.csv",
            help="Path to the CSV source file",
        )

    def handle(self, *args, **options):
        if not os.path.exists(options["file"]):
            logger.warning(f"Cannot find the file named {options['file']} let's create it")
            with open(os.path.join(options["file"]), 'w+', encoding='utf-8', newline='') as data_file:
                data = csv.DictWriter(data_file, fieldnames=['French_keywords', 'English_keywords'], delimiter='\t')
                data.writeheader()

                qs_dict = Keyword.objects.all().values().order_by('keyword')
                i = 0
                for row in qs_dict:
                    data.writerow({'French_keywords': row['keyword'], 'English_keywords': 'To translate'})
                    i += 1
                data_file.close()
            logger.info(f"{i} keywords have been added to the new file named {options['file']}")
        else:
            with open(os.path.join(options["file"]), encoding='utf-8', newline='', mode='r+') as data_file:
                data = csv.DictReader(data_file, delimiter='\t')

                count = 0
                untranslated_nb = 0
                # Queryset that content the keywords of DB
                qs_dict = Keyword.objects.all().values().order_by('keyword')
                file_dict = list(data)  # Convert data in csv file
                # Convert dict file to list and assign to `dict_to_list_file_fr` and `dict_to_list_file_en`
                dict_to_list_file_fr = [line_file['French_keywords'] for line_file in file_dict]
                dict_to_list_file_en = [line_file['English_keywords'] for line_file in file_dict]
                # Convert queryset to list and assign to `dict_to_list_qs`
                dict_to_list_qs = [item_qs['keyword'] for item_qs in qs_dict]
                # make the diff and assign to `diff_list` (Content the keywords that we need to translate).
                diff_list = list((set(dict_to_list_qs) - set(dict_to_list_file_fr)) - set(dict_to_list_file_en))

                untranslated = [[line, 'To translate'] for line in diff_list]  # Contents untranslated keywords
                writer_object = csv.writer(data_file, delimiter='\t')
                for elt in untranslated:
                    writer_object.writerow(elt)
                    untranslated_nb += 1
                data_file.close()
                logger.info(f"{untranslated_nb} Items have been added to the csv file {options['file']}")

                en_word_list = [
                    row_file['English_keywords'] for row_file in file_dict
                ]  # Assign english keywords in `en_word_list`

                # if not any(word == 'To translate' for word in en_word_list):
                for line in file_dict:
                    key_db = Keyword.objects.filter(keyword__exact=line['French_keywords']).first()
                    if key_db != line['English_keywords'] and key_db is not None:
                        if line['English_keywords'] != 'To translate':
                            key_db.keyword = line['English_keywords']
                            key_db.save()
                            count += 1
                        else:
                            logger.warning(f"{line['French_keywords']} has to be translated!")
                    else:
                        logger.warning(f"{line['French_keywords']} has already been translated!")
                logger.info(f"{count} Items have been updated")
