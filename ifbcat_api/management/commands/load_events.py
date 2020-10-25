import datetime
import os
import csv
import pytz
from tqdm import tqdm
from django.db.transaction import atomic
from django.utils.timezone import make_aware
from django.core.management import BaseCommand
from ifbcat_api.model.event import *

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    def handle(self, *args, **options):
        Event.objects.all().delete()
        # print(data_folder, 'data_folder')
        with open(options["file"], encoding='utf-8') as data_file:
            print(data_file.name)
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)
            # count number of lines
            data_len = len(list(data))
            data_file.seek(0)
            next(data)
            # do the work
            for data_object in tqdm(data, total=data_len):
                if data_object == []:
                    continue  # Check for empty lines
                event_name = data_object[0]
                event_type = data_object[1]
                event_description = data_object[2]
                if data_object[3]:
                    if "to" in data_object[3]:
                        event_start_date = datetime.datetime.strptime(
                            data_object[3].split(" to ")[0], "%d-%m-%Y"
                        )  # .strftime("%Y-%m-%d")
                        event_start_date = make_aware(event_start_date, timezone=pytz.timezone('Europe/Paris'))
                        event_end_date = datetime.datetime.strptime(data_object[3].split(" to ")[1], "%d-%m-%Y")
                        event_end_date = make_aware(event_end_date, timezone=pytz.timezone('Europe/Paris'))
                    else:
                        event_start_date = datetime.datetime.strptime(
                            data_object[3], "%d-%m-%Y"
                        )  # .strftime("%Y-%m-%d")
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
                        logo_url=event_logo,
                        type=event_type,
                        description=event_description,
                        city=event_location,
                        homepage=event_link,
                        #organizer=event_organizer,
                        #sponsoredBy=event_sponsors,
                    )
                    event.save()

                    dates = EventDate.objects.create(
                            dateStart = event_start_date,
                            dateEnd = event_end_date)
                    event.dates.add(dates)

                    #for organizer in event_organizer.split(','):
                    #    organisation = Organisation.objects.create(
                    #            name = organizer)
                    #    event.organisedByOrganisations.add(organisation)
                    #sponsoredBy = EventSponsor.objects.create(

                except Exception as e:
                    print(data_object)
                    raise e

