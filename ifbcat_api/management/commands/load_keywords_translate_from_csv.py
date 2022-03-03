import logging
import os

from django.core.management import BaseCommand, call_command
from django.db import IntegrityError

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
        call_command('cleanup_catalog')
        trans = dict()
        to_add = set()

        # Read the file
        try:
            with open(os.path.join(options["file"]), mode='r', encoding='utf-8') as file:
                for line in file.readlines():
                    line_tab = line.split(';')
                    en = line_tab[1].strip()
                    trans[line_tab[0].strip()] = en
        except FileNotFoundError:
            with open(os.path.join(options["file"]), mode='w', encoding='utf-8', newline='') as file:
                file.write('French;English\n')

        # Translation
        for kw in Keyword.objects.exclude(keyword__in=trans.values()):
            kw_keyword = kw.keyword.strip()
            if len(kw_keyword) == 0:
                continue
            try:
                kw.keyword = trans[kw_keyword]
                if len(kw.keyword) > 0:
                    kw.save()
            except IntegrityError:
                print(f'Cannot translate {kw} as target kw already exists')
            except KeyError:
                to_add.add(kw_keyword)

        # write the file
        with open(os.path.join(options["file"]), mode='a+', encoding='utf-8', newline='') as file:
            for kw in to_add:
                file.write(f'{kw};\n')
