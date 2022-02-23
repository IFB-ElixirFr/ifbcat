import csv
import logging
import os
import re
from functools import reduce

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from ifbcat_api.management.commands.load_events import parse_date
from ifbcat_api.management.commands.load_users import find_user
from ifbcat_api.model.event import Event
from ifbcat_api.model.misc import Licence
from ifbcat_api.model.team import Team
from ifbcat_api.models import Keyword
from ifbcat_api.models import TrainingMaterial

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--training-materials",
            default="import_data/training_materials.csv",
            type=str,
            help="Path to the CSV source file",
        )

    def handle(self, *args, **options):
        for firstname, lastname in [
            ('Claire', 'Rioualen'),
            ('Carl', 'Hermann'),
            ('Stéphanie', 'Le Gras'),
            ('Abdulrahman', 'Azab'),
            ('Rafa', 'C. Jimenez'),
            ('A.', 'Murat Eren'),
        ]:
            get_user_model().objects.get_or_create(
                firstname=firstname,
                lastname=lastname,
                defaults=dict(email=f"{firstname}.{lastname.replace(' ','')}@missing.none"),
            )
        with open(os.path.join(options["training_materials"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)
            # do the work
            for data_object in data:
                if data_object == []:
                    continue  # Check for empty lines
                for raw, corrected in [
                    ("&", "-"),
                    (".", "-"),
                    ("/", " - "),
                    ("—", " - "),
                ]:
                    data_object[0] = data_object[0].replace(raw, corrected)
                training_material_name = data_object[0]
                if training_material_name in ["Supports de cours", "Programme"]:
                    continue  # Two random materials with no relevant metadata
                training_material_description = data_object[1]
                training_material_file_name = data_object[2] or "missing.txt"
                training_material_keywords = re.split(r',|\n|;', data_object[3])  # as we do not have `blabla (aa,bb)`
                training_material_keywords_list = []
                for keyword in training_material_keywords:
                    keyword = keyword.strip()
                    if len(keyword) < 2:
                        continue
                    training_material_keyword, created = Keyword.objects.get_or_create(keyword=keyword)
                    training_material_keywords_list.append(training_material_keyword)
                    display_format = "\nKeyword, {}, has been saved."
                    logger.debug(display_format.format(training_material_keyword))

                if data_object[4] != "nan" and len(data_object[4]) > 0:
                    training_material_licence, created = Licence.objects.get_or_create(name=data_object[4])
                else:
                    training_material_licence = None
                try:
                    training_event = Event.objects.filter(name__iexact=data_object[5].strip()).get()
                except Event.DoesNotExist:
                    training_event = None
                if data_object[6]:
                    training_material_publication_date = parse_date(data_object[6])
                else:
                    training_material_publication_date = None
                # training_material_target_audience = data_object[7]
                training_material_url_file = data_object[8]
                maintainers = []
                providers = []
                data_object[9] = data_object[9].strip()
                for raw, corrected in [
                    ("PRAVI", "PRABI"),
                    ("Jaces Van Helden", "Jacques Van Helden"),
                    ("J van Helden", "Jacques Van Helden"),
                    ("S Le Gras", "S. Le Gras"),
                    ('N.Lapalu', 'N. Lapalu'),
                ]:
                    data_object[9] = data_object[9].replace(raw, corrected)
                if data_object[9] == "PRABI":
                    data_object[9] = "PRABI-AMSB"

                for author_str in data_object[9].split(','):
                    if len(data_object[9]) == 0:
                        continue
                    try:
                        providers.append(Team.objects.get(name=author_str))
                        continue
                    except Team.DoesNotExist:
                        pass

                    author_array = author_str.strip().split(' ')
                    if author_str in [
                        'Unknown',
                        'A. Lermine',
                    ]:
                        continue
                    user = find_user(
                        author_array[0],
                        ' '.join(author_array[1:]),
                        logger_fcn=logger.debug,
                        allow_firstname_first_letter_only=True,
                    )
                    if user:
                        maintainers.append(user)
                    else:
                        user = find_user(author_array[-1], ' '.join(author_array[:-1]), logger_fcn=logger.debug)
                        if user:
                            maintainers.append(user)
                        else:
                            if len(author_array) == 2:
                                user = get_user_model().objects.create(
                                    firstname=author_array[0],
                                    lastname=author_array[1],
                                    email=f"{'.'.join(author_array)}@missing.none",
                                )
                                maintainers.append(user)
                            elif len(author_array) == 3:
                                user = get_user_model().objects.create(
                                    firstname=author_array[0],
                                    lastname=' '.join(author_array[1:]),
                                    email=f"{'.'.join(author_array)}@missing.none",
                                )
                                maintainers.append(user)
                            else:
                                logger.error(f"Couldn't find {data_object[9]} for {training_material_name}")

                try:
                    if training_material_url_file.endswith('…'):
                        training_material_description += '\n\n' + training_material_url_file
                        logger.warning("training_material_url_file invalid:" + training_material_url_file)
                        training_material_url_file = "https://catalogue.france-bioinformatique.fr/404"
                    if training_material_url_file is None or len(training_material_url_file) == 0:
                        logger.warning("no training_material_url_file for " + training_material_name)
                        training_material_url_file = "https://catalogue.france-bioinformatique.fr/404"
                    training_material, created = TrainingMaterial.objects.update_or_create(
                        name=training_material_name,
                        defaults=dict(
                            description=training_material_description,
                            fileName=training_material_file_name,
                            licence=training_material_licence,
                            dateCreation=training_material_publication_date,
                            fileLocation=training_material_url_file,
                        ),
                    )
                    # training_material.clean_fields()
                    for o in training_material_keywords_list:
                        training_material.keywords.add(o)
                    for o in maintainers:
                        training_material.maintainers.add(o)
                    for o in providers:
                        training_material.providedBy.add(o)
                    if training_event:
                        training_event.trainingMaterials.add(training_material)
                    logger.debug(f'Training "{training_material}" has been saved.')
                except Exception as ex:
                    logger.error(f"Something went wrong saving this training: {data_object}")
                    logger.error(ex)
                    raise ex
