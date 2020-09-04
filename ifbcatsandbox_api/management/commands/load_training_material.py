import datetime
import os
import csv
import pytz

from django.db.transaction import atomic
from django.utils.timezone import make_aware
from django.core.management import BaseCommand
from database.models import Training_material
from database.models import Keyword
from catalogue.settings import BASE_DIR
class Command(BaseCommand):
    def import_materiel_formation_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, 'import_data', 'resources/csv_file')
        Training_material.objects.all().delete()
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "training_material.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    data = csv.reader(data_file)
                    # skip first line as there is always a header
                    next(data)
                    #do the work
                    for data_object in data:
                        if data_object == []:
                            continue  # Check for empty lines
                        training_material_name = data_object[0]
                        training_material_description = data_object[1]
                        training_material_file_name = data_object[2]
                        training_material_keywords = data_object[3].split(",")
                        training_material_keywords_list = []
                        training_material_keyword = ""
                        for keyword in training_material_keywords:
                            if len(keyword) > 2:

                                try:

                                    training_material_keyword, created = Keyword.objects.get_or_create(
                                        name=keyword,

                                    )
                                    training_material_keyword.save()
                                    training_material_keywords_list.append(training_material_keyword)
                                    display_format = "\nKeyword, {}, has been saved."
                                    print(display_format.format(training_material_keyword))
                                except Exception as ex:
                                    print(str(ex))
                                    msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(
                                        training_material_keyword, str(ex))
                                    print(msg)


                        training_material_licence = data_object[4]
                        training_material_event_link = data_object[5]
                        if data_object[6]:
                            training_material_publication_date = datetime.datetime.strptime(data_object[6].split(" to ")[0], "%d-%m-%Y")#.strftime("%Y-%m-%d")
                            training_material_publication_date = make_aware(training_material_publication_date, timezone=pytz.timezone('Europe/Paris'))
                        else:
                            training_material_publication_date = None
                        print (training_material_publication_date)
                        training_material_target_audience = data_object[7]
                        training_material_url_file = data_object[8]

                        training_material = ""
                        try:
                            training_material, created = Training_material.objects.get_or_create(
                                name=training_material_name,
                                description=training_material_description,
                                file_name = training_material_file_name,
                                licence = training_material_licence,
                                event_link = training_material_event_link,
                                publication_date = training_material_publication_date,
                                target_audience = training_material_target_audience,
                                url_file = training_material_url_file,

                            )

                            if created:
                                training_material.save()


                                display_format = "\nTraining material, {}, has been saved."
                                print(display_format.format(training_material))
                                for keyword in training_material_keywords_list:
                                    training_material.keywords.add(keyword)

                                training_material.save()

                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this training material: {}\n{}".format(training_material, str(ex))
                            print(msg)

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_materiel_formation_from_csv_file()
