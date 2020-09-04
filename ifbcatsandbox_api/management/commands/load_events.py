import datetime
import os
import csv
import pytz
from tqdm import tqdm

from django.db.transaction import atomic
from django.utils.timezone import make_aware

from django.core.management import BaseCommand
from database.models import Event
from catalogue.settings import BASE_DIR
class Command(BaseCommand):
    def import_events_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, 'import_data', 'resources/csv_file')
        Event.objects.all().delete()
        # print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "events.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    print(data_file.name)
                    data = csv.reader(data_file)
                    # skip first line as there is always a header
                    next(data)
                    #count number of lines
                    data_len = len(list(data))
                    data_file.seek(0)
                    next(data)
                    #do the work
                    for data_object in tqdm(data, total=data_len):
                        if data_object == []:
                            continue  # Check for empty lines
                        event_name = data_object[0]
                        event_type = data_object[1]
                        event_description = data_object[2]
                        if data_object[3]:
                            if "to" in data_object[3]:
                                event_start_date = datetime.datetime.strptime(data_object[3].split(" to ")[0], "%d-%m-%Y")#.strftime("%Y-%m-%d")
                                event_start_date = make_aware(event_start_date, timezone=pytz.timezone('Europe/Paris'))
                                event_end_date = datetime.datetime.strptime(data_object[3].split(" to ")[1], "%d-%m-%Y")
                                event_end_date = make_aware(event_end_date, timezone=pytz.timezone('Europe/Paris'))
                            else:
                                event_start_date = datetime.datetime.strptime(data_object[3], "%d-%m-%Y")#.strftime("%Y-%m-%d")
                                event_start_date = make_aware(event_start_date, timezone=pytz.timezone('Europe/Paris'))
                                event_end_date = None
                        else:
                            event_start_date = None
                            event_end_date = None

                        event_location = data_object[4]
                        event_link = data_object[5]
                        event_organizer = data_object[6]
                        event_sponsors = data_object[7]
                        event_logo = data_object[8]

                        try:
                            event = Event.objects.create(
                                name=event_name,
                                logo=event_logo,
                                event_type=event_type,
                                description=event_description,
                                start_date=event_start_date,
                                end_date=event_end_date,
                                location=event_location,
                                link=event_link,
                                organizer=event_organizer,
                                sponsors=event_sponsors,
                            )
                        except Exception as e:
                            print(data_object)
                            raise e

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_events_from_csv_file()
