import os
import csv
import re

from django.core.management import BaseCommand
from database.models import Platform
from catalogue.settings import BASE_DIR


class Command(BaseCommand):
    def import_infra_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, 'import_data', 'resources/csv_file')
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "infrastructures.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    data = csv.reader(data_file)
                    # skip first line as there is always a header
                    next(data)
                    # do the work
                    for data_object in data:
                        if data_object == []:
                            continue  # Check for empty lines
                        pf_name = data_object[0]
                        pf_infrastructure_type = data_object[1]
                        pf_useful_storage_capacity = data_object[2]
                        pf_cpu_number = data_object[3].replace(" cores", "").replace(" ", "") or 0
                        pf_data_collection = data_object[4]
                        pf_cpu_hour_per_year = data_object[5]
                        pf_informatics_tools = data_object[6]
                        pf_users_number = data_object[7].replace(" ", "") or 0
                        pf_support_condition = data_object[8]
                        pf_server_description = data_object[9]
                        pf_title_project_support = data_object[10]
                        pf_description_projects_help = data_object[11]
                        pf_accompanied_project = data_object[12]
                        pf_hosted_projects = data_object[13]
                        pf_publications = data_object[14]
                        platform = ""
                        try:
                            Platform.objects.filter(name=pf_name).update(
                                infrastructure_type=pf_infrastructure_type,
                                useful_storage_capacity=pf_useful_storage_capacity,
                                cpu_number=pf_cpu_number,
                                data_collection=pf_data_collection,
                                cpu_hour_per_year=pf_cpu_hour_per_year,
                                informatics_tools=pf_informatics_tools,
                                users_number=pf_users_number,
                                support_condition=pf_support_condition,
                                server_description=pf_server_description,
                                title_project_support=pf_title_project_support,
                                description_projects_help=pf_description_projects_help,
                                accompanied_project=pf_accompanied_project,
                                hosted_projects=pf_hosted_projects,
                                publications=pf_publications,
                            )

                            display_format = "\ninfrastructure, {}, has been saved."
                            print(display_format.format(pf_name))

                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this platform: {}\n{}".format(platform, str(ex))
                            print(msg)

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_infra_from_csv_file()
