import logging

import pandas as pd
from django.core.management import BaseCommand

from ifbcat_api import models
from ifbcat_api.management.commands.load_bioinformatics_teams import to_none_when_appropriate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import Teams"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    def handle(self, *args, **options):
        df = pd.read_csv(options["file"], sep=",")
        # models.UserProfile.objects.all().delete()
        for index, row in df.iterrows():
            try:
                try:
                    bt = models.UserProfile.objects.get(
                        firstname__unaccent__iexact=row["firstname"].strip(),
                        lastname__unaccent__iexact=row["lastname"].strip(),
                    )
                except models.UserProfile.DoesNotExist:
                    bt = models.UserProfile()
                    bt.firstname = row["firstname"].strip()
                    bt.lastname = row["lastname"].strip()
                email = row["email"].strip()
                if email != "todo@todo.com":
                    bt.email = row["email"].strip()
                elif bt.email is None or bt.email == "":
                    bt.email = '%s.%s@todo.com' % (
                        bt.firstname.strip().replace(" ", "-"),
                        bt.lastname.strip().replace(" ", "-"),
                    )
                    logger.warning("Missing email, building fake one: %s" % bt.email)
                else:
                    logger.info("Ignoring fake email %s" % email)
                bt.homepage = to_none_when_appropriate(row["homepage"])
                bt.save()
            except Exception as e:
                logger.error("Failed with line %i:%s" % (index, str(row)))
                raise e
