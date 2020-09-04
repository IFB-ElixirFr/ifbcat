import os
import csv
import pytz

from django.db.transaction import atomic
from django.utils.timezone import make_aware
import datetime
from django.core.management import BaseCommand
from database.models import Formation
from database.models import Keyword
from catalogue.settings import BASE_DIR
class Command(BaseCommand):
    def import_formations_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, 'import_data', 'resources/csv_file')
        Formation.objects.all().delete()
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "training.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    data = csv.reader(data_file)
                    # skip first line as there is always a header
                    next(data)
                    #do the work
                    for data_object in data:
                        if data_object == []:
                            continue  # Check for empty lines
                        formation_name = data_object[0]
                        formation_type = data_object[2]
                        formation_description = data_object[4]
                        formation_keywords = data_object[5].split("\n")
                        formation_keywords_list = []
                        formation_keyword = ""
                        for keyword in formation_keywords:
                            if len(keyword) > 2:

                                try:

                                    formation_keyword, created = Keyword.objects.get_or_create(
                                        name=keyword,

                                    )
                                    formation_keyword.save()
                                    formation_keywords_list.append(formation_keyword)
                                    display_format = "\nKeyword, {}, has been saved."
                                    print(display_format.format(formation_keyword))
                                except Exception as ex:
                                    print(str(ex))
                                    msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(
                                        formation_keyword, str(ex))
                                    print(msg)

                        if data_object[7]:
                            if "to" in data_object[7]:
                                formation_start_date = datetime.datetime.strptime(data_object[7].split(" to ")[0], "%d-%m-%Y")#.strftime("%Y-%m-%d")
                                formation_start_date = make_aware(formation_start_date, timezone=pytz.timezone('Europe/Paris'))
                                formation_end_date = datetime.datetime.strptime(data_object[7].split(" to ")[1], "%d-%m-%Y")
                                formation_end_date = make_aware(formation_end_date, timezone=pytz.timezone('Europe/Paris'))
                            else:
                                formation_start_date = datetime.datetime.strptime(data_object[7], "%d-%m-%Y")#.strftime("%Y-%m-%d")
                                formation_start_date = make_aware(formation_start_date, timezone=pytz.timezone('Europe/Paris'))
                                formation_end_date = None
                        else:
                            formation_start_date = None
                            formation_end_date = None
                        formation_acces_condition = data_object[8]
                        formation_link = data_object[9]
                        formation_location = data_object[10]
                        formation_organizer = data_object[11]
                        formation_sponsors = data_object[12]
                        if data_object[13]:
                            formation_number_people_trained = data_object[13].split("/ ")[0]
                        else:
                            formation_number_people_trained: None
                        if data_object[14]:
                            formation_number_of_academic_participants = data_object[14]
                        else:
                            formation_number_of_academic_participants = None
                        if data_object[15]:
                            formation_number_of_non_academic_participants = data_object[15]
                        else:
                            formation_number_of_non_academic_participants = None

                        if data_object[16]:
                            formation_training_time = data_object[16]
                        else:
                            formation_training_time = None
                        formation_participation = data_object[17]
                        formation_training_level = data_object[18]
                        formation_training_operator = data_object[19]
                        if data_object[20]:
                            formation_number_of_sessions = data_object[20]
                        else:
                            formation_number_of_sessions = None
                        formation_recurrence = data_object[21]
                        if data_object[22]:
                            formation_satisfaction_rate = data_object[22].split("%")[0]
                        else:
                            formation_satisfaction_rate = None
                        #formation_platform = data_object[23]

                        formation= ""

                        try:
                            formation, created = Formation.objects.get_or_create(
                                name=formation_name,
                                formation_type=formation_type,
                                description = formation_description,
                                start_date = formation_start_date,
                                end_date = formation_end_date,
                                location=formation_location,
                                access_conditions= formation_acces_condition,
                                link = formation_link,
                                organizer = formation_organizer,
                                sponsors = formation_sponsors,
                                number_people_trained= formation_number_people_trained,
                                number_of_academic_participants = formation_number_of_academic_participants,
                                number_of_non_academic_participants = formation_number_of_non_academic_participants,
                                training_time = formation_training_time,
                                participation = formation_participation,
                                training_level = formation_training_level,
                                training_operator = formation_training_operator,
                                number_of_sessions = formation_number_of_sessions,
                                recurrence = formation_recurrence,
                                satisfaction_rate = formation_satisfaction_rate,
                                #platform = formation_platform,

                            )

                            if created:
                                formation.save()


                                display_format = "\nFormation, {}, has been saved."
                                print(display_format.format(formation))
                                for keyword in formation_keywords_list:
                                    formation.keywords.add(keyword)

                                formation.save()


                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this tool: {}\n{}".format(formation, str(ex))
                            print(msg)

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_formations_from_csv_file()
