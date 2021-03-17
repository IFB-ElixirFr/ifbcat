import csv
import logging
import os

from django.core.management import BaseCommand

from ifbcat_api.models import Field
from ifbcat_api.models import Keyword
from ifbcat_api.models import Team

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    def handle(self, *args, **options):
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)
            # do the work
            for data_object in data:
                if data_object == []:
                    continue  # Check for empty lines
                pf_name = data_object[0]
                pf_activity_areas = data_object[1].split("\n")
                pf_activity_areas_list = []
                activity_area = ""
                for pf_activity_area in pf_activity_areas:
                    if len(pf_activity_area) > 2:

                        try:

                            activity_area, created = Field.objects.get_or_create(
                                field=pf_activity_area,
                            )
                            pf_activity_areas_list.append(activity_area)
                            if created:
                                logger.debug(f'Field (i.e Activity area) "{activity_area}" has been saved.')
                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this activity_area: {}\n{}".format(
                                activity_area, str(ex)
                            )
                            print(msg)

                pf_description_expertises = data_object[2]
                pf_keywords = data_object[3].split("\n")
                pf_keywords_list = []
                pf_keyword = ""
                for keyword in pf_keywords:
                    if len(keyword) > 2:

                        try:

                            pf_keyword, created = Keyword.objects.get_or_create(
                                keyword=keyword,
                            )
                            # pf_keyword.save()
                            pf_keywords_list.append(pf_keyword)
                            if created:
                                logger.debug(f'Keyword "{pf_keyword}" has been saved.')
                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(pf_keyword, str(ex))
                            print(msg)

                platform = ""
                try:
                    if Team.objects.filter(name=pf_name).exists():
                        platform, created = Team.objects.get_or_create(name=pf_name)

                        platform.description = pf_description_expertises

                        for an_activity_area in pf_activity_areas_list:
                            platform.fields.add(an_activity_area)
                        for a_keyword in pf_keywords_list:
                            platform.keywords.add(a_keyword)
                        platform.save()
                        if created:
                            logger.debug(f'Team (i.e Platform) "{platform}" has been saved.')

                except Exception as ex:
                    print(str(ex))
                    msg = "\n\nSomething went wrong saving this platform: {}\n{}".format(platform, str(ex))
                    print(msg)
