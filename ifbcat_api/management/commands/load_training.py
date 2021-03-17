import csv
import datetime
import logging
import os

import pandas as pd
import pytz
from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from ifbcat_api.model.event import EventDate
from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team
from ifbcat_api.models import EventCost
from ifbcat_api.models import EventPrerequisite
from ifbcat_api.models import Keyword
from ifbcat_api.models import TrainingEvent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--training",
            default="import_data/training.csv",
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

        with open(os.path.join(options["training"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)
            # do the work
            for data_object in data:
                if data_object == []:
                    continue  # Check for empty lines
                training_name = data_object[0]
                training_type = data_object[2]
                training_description = data_object[4]
                training_keywords = data_object[5].split("\n")
                training_keywords_list = []
                training_keyword = ""
                for keyword in training_keywords:
                    keyword = keyword.strip()
                    if keyword == 'Aucun des termes ci-dessus ne convient':
                        continue
                    if len(keyword) > 2:

                        try:

                            training_keyword, created = Keyword.objects.get_or_create(
                                keyword=keyword,
                            )
                            training_keyword.save()
                            training_keywords_list.append(training_keyword)
                            logger.debug(f'Keyword "{training_keyword}" has been saved.')
                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(
                                training_keyword, str(ex)
                            )
                            print(msg)

                if data_object[7]:
                    if "to" in data_object[7]:
                        training_start_date = datetime.datetime.strptime(
                            data_object[7].split(" to ")[0], "%d-%m-%Y"
                        )  # .strftime("%Y-%m-%d")
                        training_start_date = make_aware(training_start_date, timezone=pytz.timezone('Europe/Paris'))
                        training_end_date = datetime.datetime.strptime(data_object[7].split(" to ")[1], "%d-%m-%Y")
                        training_end_date = make_aware(training_end_date, timezone=pytz.timezone('Europe/Paris'))
                    else:
                        training_start_date = datetime.datetime.strptime(
                            data_object[7], "%d-%m-%Y"
                        )  # .strftime("%Y-%m-%d")
                        training_start_date = make_aware(training_start_date, timezone=pytz.timezone('Europe/Paris'))
                        training_end_date = None
                else:
                    training_start_date = None
                    training_end_date = None
                training_access_condition = data_object[8]
                training_link = data_object[9]
                training_location = data_object[10]
                training_organizer = data_object[11]
                training_sponsors = data_object[12]
                if data_object[13]:
                    training_number_people_trained = data_object[13].split("/ ")[0]
                else:
                    training_number_people_trained: None
                if data_object[14]:
                    training_number_of_academic_participants = data_object[14]
                else:
                    training_number_of_academic_participants = None
                if data_object[15]:
                    training_number_of_non_academic_participants = data_object[15]
                else:
                    training_number_of_non_academic_participants = None

                if data_object[16]:
                    training_training_time = data_object[16]
                else:
                    training_training_time = None
                training_participation = data_object[17]
                training_training_level = data_object[18]
                training_training_operator = data_object[19]
                if data_object[20]:
                    training_number_of_sessions = data_object[20]
                else:
                    training_number_of_sessions = None
                training_recurrence = data_object[21]
                if data_object[22]:
                    training_satisfaction_rate = data_object[22].split("%")[0]
                else:
                    training_satisfaction_rate = None
                # training_platform = data_object[23]

                training = ""

                try:
                    training, created = TrainingEvent.objects.get_or_create(
                        name=training_name,
                        type="Training course",
                        # training_type=training_type,
                        description=training_description,
                        # start_date=training_start_date,
                        # end_date=training_end_date,
                        city=training_location,
                        accessibilityNote=training_access_condition,
                        homepage=training_link,
                        # organizer=training_organizer,
                        # sponsors=training_sponsors,
                        # number_people_trained=training_number_people_trained,
                        # number_of_academic_participants=training_number_of_academic_participants,
                        # number_of_non_academic_participants=training_number_of_non_academic_participants,
                        # training_time=training_training_time,
                        # participation=training_participation,
                        # training_level=training_training_level,
                        # training_operator=training_training_operator,
                        # number_of_sessions=training_number_of_sessions,
                        # recurrence=training_recurrence,
                        # satisfaction_rate=training_satisfaction_rate,
                        # platform = training_platform,
                    )

                    for organizer in training_organizer.split(','):
                        organizer = organizer.strip()
                        if organizer == '':
                            logger.debug(f'No organizer for {training_name}')
                        elif Organisation.objects.filter(name=organizer).exists():
                            organisation = Organisation.objects.get(name=organizer)
                            training.organisedByOrganisations.add(organisation)
                        elif organizer in mapping_organisations['drupal_name'].tolist():
                            organizer_row = mapping_organisations[mapping_organisations['drupal_name'] == organizer]
                            if not organizer_row['orgid'].isna().iloc[0]:
                                organisation = Organisation.objects.get(orgid=organizer_row['orgid'].iloc[0])
                            elif not organizer_row['ifbcat_name'].isna().iloc[0]:
                                organisation = Organisation.objects.get(name=organizer_row['ifbcat_name'].iloc[0])
                            training.organisedByOrganisations.add(organisation)

                        elif Team.objects.filter(name=organizer).exists():
                            team = Team.objects.get(name=organizer)
                            training.organisedByTeams.add(team)
                        elif organizer in mapping_teams['drupal_name'].tolist():
                            organizer_row = mapping_teams[mapping_teams['drupal_name'] == organizer]
                            team = Team.objects.get(name=organizer_row['ifbcat_name'].iloc[0])
                            training.organisedByTeams.add(team)

                        else:
                            logger.warning(f'{organizer} is not an organisation in the DB.')

                    for keyword in training_keywords_list:
                        training.keywords.add(keyword)

                    event_cost, created = EventCost.objects.get_or_create(cost=training_participation)
                    training.costs.add(event_cost)

                    # Need to check this chunk with Bryan
                    # (1
                    if training_start_date:
                        dates = EventDate.objects.filter(dateStart=training_start_date, dateEnd=training_end_date)[0]
                        if not dates:
                            dates = EventDate.objects.create(dateStart=training_start_date, dateEnd=training_end_date)

                        # get() returned more than one EventDate -- it returned 2!
                        # dates, created = EventDate.objects.get_or_create(dateStart=training_start_date, dateEnd=training_end_date)

                        training.dates.add(dates)
                    # 1)

                    if training_training_level:
                        prerequisite, created = EventPrerequisite.objects.get_or_create(
                            prerequisite=training_training_level
                        )
                        training.prerequisites.add(prerequisite)

                    # if created:
                    # training.full_clean()
                    training.save()

                    logger.debug(f'Training "{training}" has been saved.')
                except Exception as ex:
                    print(str(ex))
                    msg = "\n\nSomething went wrong saving this training: {}\n{}".format(training, str(ex))
                    print(msg)
