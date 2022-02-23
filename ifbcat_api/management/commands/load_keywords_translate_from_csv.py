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
            default="import_data/keywords_english_translate.csv",
            help="Path to the CSV source file",
        )

    def handle(self, *args, **options):
        if os.path.exists(options["file"]):
            my_dict = {}
            with open(options["file"], encoding='utf-8') as data_file:
                data = csv.reader(data_file, delimiter='\t')
                data_file.seek(0)
                next(data)  # skip first line as there is always a header we guests

                for data_object in data:
                    my_dict[data_object[0]] = data_object[1]

            qs_dict = Keyword.objects.all().order_by('keyword')
            # print(my_dict['Accessibilité de la chromatine'])
            for key in qs_dict:
                print(key.keyword, "<->", my_dict.get(key))
