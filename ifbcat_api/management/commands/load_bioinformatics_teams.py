import os
import pandas as pd

from django.core.management import BaseCommand
from ifbcat_api.models import BioinformaticsTeam, Organisation


class Command(BaseCommand):

    help = "Import Teams"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    def handle(self, *args, **options):
        df = pd.read_csv(options["file"], sep=",")
        BioinformaticsTeam.objects.all().delete()
        Organisation.objects.all().delete()
        for index, row in df.iterrows():
            bt = BioinformaticsTeam()
            bt.name = row["Nom de la plateforme"]
            bt.address = row["Adresse postale"]
            bt.save()
            for affiliation in row["Affiliation"].split(","):
                # FIXME, adding dummy contents because description and homepage are missing
                o, created = Organisation.objects.get_or_create(name=affiliation)
                if created:
                    o.name = affiliation
                    o.description = f"description for {affiliation}"
                    o.homepage = f"http://nothing.org"
                    o.full_clean()
                    o.save()
                bt.affiliatedWith.add(o)
            bt.save()


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
