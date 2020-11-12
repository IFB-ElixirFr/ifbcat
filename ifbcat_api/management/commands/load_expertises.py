import os
import csv

from django.core.management import BaseCommand
from ifbcat_api.models import Platform
from ifbcat_api.models import Activityarea
from ifbcat_api.models import Keyword
from ifbcat.settings import BASE_DIR


class Command(BaseCommand):
    def import_expertise_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, '../ifbcat-importdata')
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "expertises.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
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

                                    activity_area, created = Activityarea.objects.get_or_create(
                                        name=pf_activity_area,
                                    )
                                    activity_area.save()
                                    pf_activity_areas_list.append(activity_area)
                                    display_format = "\nKeyword, {}, has been saved."
                                    print(display_format.format(activity_area))
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
                                        name=keyword,
                                    )
                                    pf_keyword.save()
                                    pf_keywords_list.append(pf_keyword)
                                    display_format = "\nKeyword, {}, has been saved."
                                    print(display_format.format(pf_keyword))
                                except Exception as ex:
                                    print(str(ex))
                                    msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(
                                        pf_keyword, str(ex)
                                    )
                                    print(msg)

                        platform = ""
                        try:
                            print(Platform.objects.filter(name=pf_name).exists())
                            if Platform.objects.filter(name=pf_name).exists():
                                platform, created = Platform.objects.get_or_create(
                                    description_expertise=pf_description_expertises,
                                )

                                for an_activity_area in pf_activity_areas_list:
                                    platform.activity_area.add(an_activity_area)
                                for a_keyword in pf_keywords_list:
                                    platform.keywords.add(a_keyword)
                                platform.save()
                                display_format = "\nExpertise, {}, has been saved."
                                print(display_format.format(platform))

                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this platform: {}\n{}".format(platform, str(ex))
                            print(msg)

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_expertise_from_csv_file()
