import os
import csv

from django.core.management import BaseCommand
from database.models import Platform
from database.models import People
from database.models import Certificat
from catalogue.settings import BASE_DIR


class Command(BaseCommand):
    def import_plateforme_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, 'import_data', 'resources/csv_file')
        Platform.objects.all().delete()
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "platforms.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    data = csv.reader(data_file)
                    # skip first line as there is always a header
                    next(data)
                    # do the work
                    for data_object in data:
                        if data_object == []:
                            continue  # Check for empty lines
                        lead_technic_list = []
                        lead_scientific_list = []
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
                                    msg = "\n\nSomething went wrong saving this People: {}\n{}".format(
                                        lead_tech, str(ex)
                                    )
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
                                    msg = "\n\nSomething went wrong saving this People: {}\n{}".format(
                                        lead_scien, str(ex)
                                    )
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
                                    )
                                    pf_team.save()
                                    platform_team_list.append(pf_team)
                                    display_format = "\nPeople, {}, has been saved."
                                    print(display_format.format(pf_team))
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
                                affiliation=platform_affiliation,
                                website=platform_website,
                                structure=platform_structure,
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

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_plateforme_from_csv_file()
