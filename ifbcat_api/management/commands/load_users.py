import logging

import pandas as pd
from django.contrib.postgres.lookups import Unaccent
from django.core.management import BaseCommand
from django.db.models import Value, Q, Case, When, IntegerField
from django.db.models.functions import Upper, Concat, Replace

from ifbcat_api.models import UserProfile

from ifbcat_api.management.commands.load_teams import to_none_when_appropriate


logger = logging.getLogger(__name__)


def is_line_should_be_skipped(index, row):
    return row["firstname"].strip() == "Antoniewski" and row["lastname"].strip() == "Christophe"


class Command(BaseCommand):
    help = "Import Teams"

    def add_arguments(self, parser):

        parser.add_argument(
            "--by-email",
            type=str,
            help="Path to a CSV file containing at least one 'email' column, and optionally 'firstname', 'lastname', 'homepage' columns.",
            default="import_data/manual_curation/users.csv",
        )

        parser.add_argument(
            "--by-flname",
            type=str,
            help="Path to a CSV file containing at least 'firstname' and 'lastname' columns, and optionally 'homepage' column. If the file contains valid 'email', it is more appropriate to use '--by-email'",
            default="import_data/manual_curation/users_more.csv",
        )

    def handle(self, *args, **options):
        df = pd.read_csv(options["by_email"], sep=",")
        for index, row in df.iterrows():

            user, created = UserProfile.objects.get_or_create(email=row['email'].lower())
            if "firstname" in df:
                user.firstname = row["firstname"]
            if "lastname" in df:
                user.lastname = row["lastname"]
            if "homepage" in df:
                user.homepage = row["homepage"]
            user.save()

        df = pd.read_csv(options["by_flname"], sep=",")
        for index, row in df.iterrows():
            if is_line_should_be_skipped(index, row):
                continue

            try:
                user = UserProfile.objects.get(
                    firstname__unaccent__iexact=row["firstname"].strip(),
                    lastname__unaccent__iexact=row["lastname"].strip(),
                )
            except UserProfile.DoesNotExist:
                try:
                    # logger.warning("Test Search for %s %s. Make sure this user is first loaded with a valid email." % (row["firstname"],row["lastname"]))

                    user = UserProfile.objects.get(
                        firstname__search=row["firstname"].strip(),
                        lastname__search=row["lastname"].strip(),
                    )
                except UserProfile.DoesNotExist:
                    logger.warning(
                        "No matching user for lookup by first and last name for %s %s. Make sure this user is first loaded with a valid email."
                        % (row["firstname"], row["lastname"])
                    )

            except UserProfile.MultipleObjectsReturned:

                user = UserProfile.objects.filter(
                    firstname__unaccent__iexact=row["firstname"].strip(),
                    lastname__unaccent__iexact=row["lastname"].strip(),
                ).first()
                logger.warning(
                    "More than one matching user for lookup by first and last name for %s %s. Make sure this user is not loaded more than one time because of multiple emails. For now, additional informations are added to its first email %s."
                    % (row["firstname"], row["lastname"], user.email)
                )

            except Exception as e:
                logger.warning(e)

            if "homepage" in df:
                user.homepage = row["homepage"]

            # We could add function and other columns here

            user.save()
