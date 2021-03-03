import csv
import datetime
import logging
import os

from django.core.exceptions import MultipleObjectsReturned
from django.core.management import BaseCommand
from tqdm import tqdm

from ifbcat_api.model.event import *
from ifbcat_api.model.organisation import Organisation

logger = logging.getLogger(__name__)


def parse_date(date_string):
    event_start_date = datetime.datetime.strptime(date_string, "%d-%m-%Y")
    # event_start_date = make_aware(event_start_date, timezone=pytz.timezone('Europe/Paris'))
    event_start_date = event_start_date.strftime("%Y-%m-%d")
    return event_start_date


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    def handle(self, *args, **options):
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)
            # count number of lines
            data_len = len(list(data))
            data_file.seek(0)
            next(data)
            # do the work#
            for data_object in tqdm(data, total=data_len):
                if data_object == []:
                    continue  # Check for empty lines
                event_name = data_object[0]
                event_type = data_object[1]
                event_description = data_object[2]
                if data_object[3]:
                    if "to" in data_object[3]:
                        data_object[3] = data_object[3].split(" to ")
                        event_start_date = parse_date(data_object[3][0])
                        event_end_date = parse_date(data_object[3][1])
                    else:
                        event_start_date = parse_date(data_object[3])
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
                    event, created = Event.objects.get_or_create(
                        name=event_name,
                        defaults=dict(
                            logo_url=event_logo,
                            type=event_type,
                            description=event_description,
                            # city is only a subset of event_location for the moment
                            city=event_location,
                            homepage=event_link,
                        ),
                    )

                    try:
                        dates, created = event.dates.get_or_create(dateStart=event_start_date, dateEnd=event_end_date)
                    except MultipleObjectsReturned:
                        event.dates.all().delete()
                        dates = EventDate.objects.create(dateStart=event_start_date, dateEnd=event_end_date)

                    event.dates.add(dates)

                    for organizer in event_organizer.split(','):
                        organizer = organizer.strip()

                        if organizer == '':
                            logger.debug(f'No organizer for {event_name}')
                        elif Organisation.objects.filter(name=organizer).exists():
                            organizer_instance = Organisation.objects.get(name=organizer)
                            event.organisedByOrganisations.add(organizer_instance)
                        elif Team.objects.filter(name=organizer).exists():
                            organizer_instance = Team.objects.get(name=organizer)
                            event.organisedByTeams.add(organizer_instance)
                        else:
                            logger.error(f'{organizer} is not an organisation not team in the DB.')

                    # EventSponsors should be created before to be able to add them here to events
                    # for sponsor in event_sponsors.split(','):
                    #    sponsor=sponsor.strip()

                    #    if sponsor == '':
                    #        logger.debug(f'No sponsor for {sponsor}')

                    #    elif EventSponsor.objects.filter(name=sponsor).exists():
                    #        organisation=EventSponsor.objects.get(name=sponsor)
                    #        event.sponsoredBy.add(organisation)

                except Exception as e:
                    logger.error(data_object)
                    raise e
