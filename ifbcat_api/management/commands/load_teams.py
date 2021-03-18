import logging
import math

import pandas as pd
from django.contrib.postgres.lookups import Unaccent
from django.core.management import BaseCommand
from django.db.models import Value
from django.db.models.functions import Replace

from ifbcat_api import models
from ifbcat_api.models import Certification
from ifbcat_api.models import Organisation

logger = logging.getLogger(__name__)


def to_none_when_appropriate(e):
    if type(e) == str and e.upper() in ["NULL", "NAN"]:
        return None
    if type(e) == float and math.isnan(e):
        return None
    return e


def find_persons(first_and_last_names):
    if type(first_and_last_names) == float and math.isnan(first_and_last_names):
        return
    for p in first_and_last_names.replace(",", "\n").strip().split("\n"):
        pers = find_person(p)
        if pers:
            yield pers


def find_person(first_and_last_name):
    if type(first_and_last_name) == float and math.isnan(first_and_last_name):
        return None
    if "Non renseigné" in first_and_last_name:
        return None
    first_and_last_name = first_and_last_name.strip()
    names = first_and_last_name.split(" ")
    for i in range(1, len(names)):
        a_raw = " ".join(names[:i])
        b_raw = " ".join(names[i:])
        for f, l in [
            (a_raw, b_raw),
            (b_raw, a_raw),
            (a_raw, b_raw.replace(" ", "-")),
            (b_raw, a_raw.replace(" ", "-")),
            (a_raw.replace(" ", "-"), b_raw),
            (b_raw.replace(" ", "-"), a_raw),
            (a_raw.replace(" ", "-"), b_raw.replace(" ", "-")),
            (b_raw.replace(" ", "-"), a_raw.replace(" ", "-")),
        ]:
            try:
                return models.UserProfile.objects.get(firstname__unaccent__iexact=f, lastname__unaccent__iexact=l)
            except models.UserProfile.DoesNotExist:
                pass
            try:
                return models.UserProfile.objects.annotate(
                    f_no_quote=Replace(Unaccent("firstname"), Value("'"), Value(''))
                ).get(f_no_quote__iexact=f, lastname__unaccent__iexact=l)
            except models.UserProfile.DoesNotExist:
                pass
    print("Did not found", first_and_last_name)
    return None


class Command(BaseCommand):
    help = "Import Teams"

    def add_arguments(self, parser):
        parser.add_argument(
            "--teams",
            default="import_data/platforms.csv",
            type=str,
            help="Path to the CSV source file for teams",
        )
        parser.add_argument(
            "--mapping-organisations",
            default="import_data/manual_curation/mapping_organisations.csv",
            type=str,
            help="Path to the CSV file containing mapping for organisations between Drupal names and Ifbcat ones.",
        )

    def handle(self, *args, **options):
        df = pd.read_csv(options["teams"], sep=",")
        mapping_organisations = pd.read_csv(options["mapping_organisations"], sep=",")
        # models.Team.objects.all().delete()
        # models.Organisation.objects.all().delete()
        for index, row in df.iterrows():
            try:
                bt, _ = models.Team.objects.get_or_create(name=row["Nom de la plateforme"])
                address = row["Adresse postale"]
                zip_city = address.split('\n')[-2]
                city = zip_city.split(' ')[-1]
                bt.address = address
                bt.country = address.split('\n')[-1]
                bt.city = city
                # This plateform has no working website
                # and homepage field do not allow for none.
                # Hence this "better than nothing URL"
                if row["Nom de la plateforme"] == "PRABI-HCL":
                    homepage = "https://lbbe.univ-lyon1.fr/-90-PRABI-.html?lang=fr"
                else:
                    homepage = str(row["Website"])
                bt.homepage = homepage
                bt.logo_url = to_none_when_appropriate(str(row["Chemin"]))
                bt.homepage = to_none_when_appropriate(str(row["Website"])) or ''
                for p in find_persons(row["Responsable scientifique"]):
                    bt.scientificLeaders.add(p)
                for p in find_persons(row["Responsable technique"]):
                    bt.technicalLeaders.add(p)
                for p in find_persons(row["Equipe"]):
                    bt.members.add(p)
                for certification in row['Certificat(s)'].strip().split('\n'):
                    certification = certification.strip().replace('/', '-')
                    if certification == "Non renseigné":
                        continue
                    try:
                        c, created = Certification.objects.get_or_create(name=certification)
                        if created:
                            c.name = certification
                            c.description = f"description for {certification}"
                            c.homepage = f"http://nothing.org"
                            c.certifiedTeam = bt.name  # unsure this line does something
                            c.full_clean()
                            c.save()
                        bt.certifications.add(c)
                    except Exception as e:
                        print("Failed with %s" % certification)
                        print(e)
                affiliated_with = row["Affiliation"] + "," + row["Structure"]
                for affiliation in affiliated_with.replace("/", ",").replace("’", "'").split(","):

                    affiliation = affiliation.strip()
                    if Organisation.objects.filter(name=affiliation).exists():
                        organisation = Organisation.objects.get(name=affiliation)
                        bt.affiliatedWith.add(organisation)
                    elif affiliation in mapping_organisations['drupal_name'].tolist():
                        organizer_row = mapping_organisations[mapping_organisations['drupal_name'] == affiliation]
                        if not organizer_row['orgid'].isna().iloc[0]:
                            logger.debug(organizer_row['orgid'])
                            organisation = Organisation.objects.get(orgid=organizer_row['orgid'].iloc[0])
                        elif not organizer_row['ifbcat_name'].isna().iloc[0]:
                            logger.debug(organizer_row['orgid'])
                            organisation = Organisation.objects.get(name=organizer_row['ifbcat_name'].iloc[0])
                        bt.affiliatedWith.add(organisation)
                    elif "Non renseigné" in affiliation:
                        pass
                    else:
                        print("%s is not a known organisation" % affiliation)
                for affiliation in row["Structure"].replace("/", ",").replace("’", "'").split(","):
                    affiliation = affiliation.strip()
                    try:
                        o = Organisation.objects.get(name=affiliation)
                        bt.fundedBy.add(o)
                    except Exception as e:
                        print("Failed with %s" % affiliation)
                bt.save()
            except Exception as e:
                print("Failed with line %i:%s; %s" % (index, str(row), str(e)))
                raise e


"""
            lead_technic_list= []
            lead_scientific_list= []
            platform_certificats_list = []
            platform_team_list = []
            platform_name = data_object[0]
            platform_adress = data_object[1]
            platform_affiliation = data_object[2]
            platform_website = data_object[3]
            lead_technic_name = data_object[4].split("\n")
            lead_tech = ""
            for lead_technic in lead_technic_name:
                if len(lead_technic) > 4:
                    try:

                        lead_tech, created = People.objects.get_or_create(
                            name=lead_technic,

                        )
                        lead_tech.save()
                        lead_technic_list.append(lead_tech)
                        display_format = "\nPeople, {}, has been saved."
                        print(display_format.format(lead_tech))
                    except Exception as ex:
                        print(str(ex))
                        msg = "\n\nSomething went wrong saving this People: {}\n{}".format(lead_tech, str(ex))
                        print(msg)

            lead_scientific_name = data_object[5].split("\n")
            lead_scien = ""
            for lead_scientific in lead_scientific_name:
                if len(lead_scientific) > 4:
                    try:

                        lead_scien, created = People.objects.get_or_create(
                            name=lead_scientific,

                        )
                        lead_scien.save()
                        lead_scientific_list.append(lead_scien)
                        display_format = "\nPeople, {}, has been saved."
                        print(display_format.format(lead_scien))
                    except Exception as ex:
                        print(str(ex))
                        msg = "\n\nSomething went wrong saving this People: {}\n{}".format(lead_scien, str(ex))
                        print(msg)

            platform_certificat_name = data_object[6].split("\n")
            pf_cert = ""
            for platform_certif in platform_certificat_name:
                if len(platform_certif) > 2:
                    try:
                        pf_cert, created = Certificat.objects.get_or_create(
                            name=platform_certif,

                        )
                        pf_cert.save()
                        platform_certificats_list.append(pf_cert)
                        display_format = "\nPeople, {}, has been saved."
                        print(display_format.format(pf_cert))
                    except Exception as ex:
                        print(str(ex))
                        msg = "\n\nSomething went wrong saving this People: {}\n{}".format(pf_cert, str(ex))
                        print(msg)

            platform_structure = data_object[7]

            platform_teams_name = data_object[8].split("\n")
            pf_team = ""
            for platform_team in platform_teams_name:
                if len(platform_team) > 2:
                    try:
                        pf_team, created = People.objects.get_or_create(
                            name=platform_team,

                        pf_team.save()
                        platform_team_list.append(pf_team)
                        display_format = "\nPeople, {}, has been saved."
                        print(display_format.format(pf_team))
                        )
                    except Exception as ex:
                        print(str(ex))
                        msg = "\n\nSomething went wrong saving this Team: {}\n{}".format(pf_team, str(ex))
                        print(msg)

            platform_logo = data_object[9]
            platform = ""
            try:

                platform, created = Platform.objects.get_or_create(
                    name=platform_name,
                    logo=platform_logo,
                    address=platform_adress,
                    affiliation = platform_affiliation,
                    website = platform_website,
                    structure = platform_structure,
                )

                if created:
                    platform.save()

                    display_format = "\nPlateforme, {}, has been saved."
                    print(display_format.format(platform))
                    for lead_scientif in lead_scientific_list:
                        platform.scientific_leader.add(lead_scientif)
                    for lead_technique in lead_technic_list:
                        platform.technical_leader.add(lead_technique)
                    for platform_certif in platform_certificats_list:
                        platform.certificate.add(platform_certif)
                    for platform_team in platform_team_list:
                        platform.team.add(platform_team)

                    platform.save()

            except Exception as ex:
                print(str(ex))
                msg = "\n\nSomething went wrong saving this platform: {}\n{}".format(platform, str(ex))
                print(msg)
"""
