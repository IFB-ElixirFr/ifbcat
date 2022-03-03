import logging
import os

from django.core.management import BaseCommand, call_command
from django.db import IntegrityError

from ifbcat_api.misc import get_usage_in_related_field
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
        pending_validation = set()
        keyword_attrs = get_usage_in_related_field(Keyword.objects.all())
        translated, merged = 0, 0

        # Read the file
        try:
            with open(os.path.join(options["file"]), mode='r', encoding='utf-8') as file:
                for line in file.readlines():
                    line_tab = [s.strip() for s in line.split(';')]
                    en = line_tab[1]
                    if line_tab[2] == "True":
                        trans[line_tab[0]] = en
                    else:
                        pending_validation.add(line_tab[0])
        except FileNotFoundError:
            with open(os.path.join(options["file"]), mode='w', encoding='utf-8', newline='') as file:
                file.write('French;English;Validated\n')

        # Translation
        for kw in Keyword.objects.exclude(keyword__in=trans.values()):
            kw_keyword = kw.keyword.strip()
            if len(kw_keyword) == 0:
                continue
            try:
                kw.keyword = trans[kw_keyword]
                if len(kw.keyword) > 0:
                    kw.save()
                    translated += 1
            except IntegrityError:
                for _, attr_name, reverse_name in keyword_attrs:
                    # for all instance pointer by attr_name
                    # r is a Team for example
                    for r in getattr(kw, attr_name).all():
                        # getattr(r, reverse_name) == myTeam.keywords
                        # we add the already-in-english keyword to the team
                        getattr(r, reverse_name).add(Keyword.objects.get(keyword=trans[kw_keyword]))
                kw.delete()
                merged += 1
            except KeyError:
                to_add.add(kw_keyword)

        try:
            from translate import Translator

            translator = Translator(to_lang="en", from_lang="autodetect", email="contact@france-bioinformatique.fr")
        except ImportError:
            logging.warning("translate package not found, if we had it we could have tried to translate keywords")
            translator = None
        # write the file
        with open(os.path.join(options["file"]), mode='a+', encoding='utf-8', newline='') as file:
            for kw in to_add - pending_validation:
                guess = ""
                if translator:
                    guess = translator.translate(kw)
                    if "MYMEMORY WARNING" in guess:
                        # We hit the limit
                        translator = None
                        guess = ""
                file.write(f'{kw};{guess};{False}\n')
        call_command('cleanup_catalog')
        logger.info(
            f'{translated} keyword translated, '
            f'{merged} were merged, '
            f'{len(to_add - pending_validation)} have been added to the translation file, '
            f'{len( pending_validation)} are still pending validation/translation'
        )
