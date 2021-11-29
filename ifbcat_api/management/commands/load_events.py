import csv
import datetime
import logging
import os

import pandas as pd
from django.core.management import BaseCommand
from tqdm import tqdm

from ifbcat_api.model.event import *
from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team

logger = logging.getLogger(__name__)


def parse_date(date_string):
    event_start_date = datetime.datetime.strptime(date_string, "%d-%m-%Y")
    # event_start_date = make_aware(event_start_date, timezone=pytz.timezone('Europe/Paris'))
    event_start_date = event_start_date.strftime("%Y-%m-%d")
    return event_start_date


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--events",
            default="import_data/events.csv",
            type=str,
            help="Path to the CSV source file",
        )
        parser.add_argument(
            "--mapping-organisations",
            default="import_data/manual_curation/mapping_organisations.csv",
            type=str,
            help="Path to the CSV file containing mapping for organisations between Drupal names and Ifbcat ones.",
        )
        parser.add_argument(
            "--mapping-teams",
            default="import_data/manual_curation/mapping_teams.csv",
            type=str,
            help="Path to the CSV file containing mapping for teams between Drupal names and Ifbcat ones.",
        )

    def handle(self, *args, **options):
        mapping_organisations = pd.read_csv(options["mapping_organisations"], sep=",")
        mapping_teams = pd.read_csv(options["mapping_teams"], sep=",")

        with open(os.path.join(options["events"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)
            # count number of lines
            data_len = len(list(data))
            data_file.seek(0)
            next(data)
            # do the work
            type_mapping_drupal_to_api = {
                'Formation': 'Training course',
                'Réunion': 'Meeting',
                'Atelier': 'Workshop',
                'Conférence': 'Conference',
                'Autre': 'Other',
                '': 'Other',
            }

            for data_object in tqdm(data, total=data_len):
                if data_object == []:
                    continue  # Check for empty lines
                event_name = data_object[0]
                event_type = type_mapping_drupal_to_api[data_object[1]]
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

                # print(get_user_model().objects.filter(is_superuser=True).first())

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

                    for organizer in event_organizer.split(','):
                        organizer = organizer.strip()
                        if organizer == '':
                            logger.debug(f'No organizer for {event_name}')
                        elif Organisation.objects.filter(name=organizer).exists():
                            organisation = Organisation.objects.get(name=organizer)
                            event.organisedByOrganisations.add(organisation)
                        elif organizer in mapping_organisations['drupal_name'].tolist():
                            organizer_row = mapping_organisations[mapping_organisations['drupal_name'] == organizer]
                            if not organizer_row['orgid'].isna().iloc[0]:
                                logger.debug(organizer_row['orgid'])
                                organisation = Organisation.objects.get(orgid=organizer_row['orgid'].iloc[0])
                            elif not organizer_row['ifbcat_name'].isna().iloc[0]:
                                logger.debug(organizer_row['orgid'])
                                organisation = Organisation.objects.get(name=organizer_row['ifbcat_name'].iloc[0])
                            event.organisedByOrganisations.add(organisation)

                        elif Team.objects.filter(name=organizer).exists():
                            team = Team.objects.get(name=organizer)
                            event.organisedByTeams.add(team)
                        elif organizer in mapping_teams['drupal_name'].tolist():
                            organizer_row = mapping_teams[mapping_teams['drupal_name'] == organizer]
                            team = Team.objects.get(name=organizer_row['ifbcat_name'].iloc[0])
                            event.organisedByTeams.add(team)

                        else:
                            logger.warning(f'{organizer} is not an organisation in the DB.')

                    for sponsor in event_sponsors.split(','):
                        sponsor = sponsor.strip()
                        if sponsor == '':
                            logger.debug(f'No sponsor for {event_name}')
                            continue
                        sponsor_instance, created = EventSponsor.objects.get_or_create(name=sponsor)
                        event.sponsoredBy.add(sponsor_instance)

                    event.save()

                except Exception as e:
                    logger.error(data_object)
                    raise e
