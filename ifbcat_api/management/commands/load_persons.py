import logging

import pandas as pd
from django.contrib.postgres.lookups import Unaccent
from django.core.management import BaseCommand
from django.db.models import Value, Q, Case, When, IntegerField
from django.db.models.functions import Upper, Concat, Replace

from ifbcat_api import models
from ifbcat_api.management.commands.load_bioinformatics_teams import to_none_when_appropriate

logger = logging.getLogger(__name__)


def is_line_should_be_skipped(index, row):
    return row["firstname"].strip() == "Antoniewski" and row["lastname"].strip() == "Christophe"


class Command(BaseCommand):
    help = "Import Teams"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")
        parser.add_argument("users", type=str, help="Path to the CSV file with the emails")

    def handle(self, *args, **options):
        df = pd.read_csv(options["file"], sep=",")
        # models.UserProfile.objects.all().delete()
        for index, row in df.iterrows():
            if is_line_should_be_skipped(index, row):
                continue
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
                except models.UserProfile.MultipleObjectsReturned:
                    bt = (
                        models.UserProfile.objects.filter(
                            firstname__unaccent__iexact=row["firstname"].strip(),
                            lastname__unaccent__iexact=row["lastname"].strip(),
                        )
                        .annotate(
                            same_email=Case(
                                When(Q(email__iexact=row["email"].strip()), then=1),
                                default=Value(0),
                                output_field=IntegerField(),
                            )
                        )
                        .order_by("-same_email")
                        .first()
                    )
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

        df = pd.read_csv(options["users"], sep=",")
        for index, row in df.iterrows():
            v = Upper(Unaccent(Value(row[1].strip())))
            fl = Concat(Upper(Unaccent("firstname")), Value(' '), Upper(Unaccent("lastname")))
            fl_no_space = Concat(
                Upper(Unaccent("firstname")),
                Value(' '),
                Replace(Upper(Unaccent("lastname")), Value(' '), Value('')),
            )
            fl_tiret_to_space = Replace(fl, Value('-'), Value(' '))
            fl_no_tiret = Replace(fl, Value('-'), Value(''))
            lf = Concat(Upper(Unaccent("lastname")), Value(' '), Upper(Unaccent("firstname")))
            lf_no_space = Concat(
                Replace(Upper(Unaccent("lastname")), Value(' '), Value('')),
                Value(' '),
                Upper(Unaccent("firstname")),
            )
            lf_tiret_to_space = Replace(lf, Value('-'), Value(' '))
            lf_no_tiret = Replace(lf, Value('-'), Value(''))
            lf_noquote = Replace(lf, Value("'"), Value(''))
            matching_users = (
                models.UserProfile.objects.annotate(fl=fl)
                .annotate(fl_no_space=fl_no_space)
                .annotate(fl_tiret_to_space=fl_tiret_to_space)
                .annotate(fl_no_tiret=fl_no_tiret)
                .annotate(lf=lf)
                .annotate(lf_no_space=lf_no_space)
                .annotate(lf_tiret_to_space=lf_tiret_to_space)
                .annotate(lf_no_tiret=lf_no_tiret)
                .annotate(lf_noquote=lf_noquote)
            )
            matching_users = matching_users.filter(
                Q(fl=v)
                | Q(fl_no_space=v)
                | Q(fl_tiret_to_space=v)
                | Q(fl_no_tiret=v)
                | Q(lf=v)
                | Q(lf_no_space=v)
                | Q(lf_tiret_to_space=v)
                | Q(lf_no_tiret=v)
                | Q(lf_noquote=v)
            )
            count = matching_users.count()
            if count == 0:
                print(f'{row[1]} is not in the db')
            elif count == 2:
                print(f'{row[1]} has too much match !!! {matching_users.all()}')
            else:
                matching_users.filter(~Q(email=row[2])).update(email=row[2])
