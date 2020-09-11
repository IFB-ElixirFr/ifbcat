import os
import csv
from django.core.management import BaseCommand
from database.models import People
from catalogue.settings import BASE_DIR


class Command(BaseCommand):
    def import_poeple_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, 'import_data', 'resources/csv_file')
        People.objects.all().delete()
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "persons.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    data = csv.reader(data_file)
                    for data_object in data:
                        l = data.line_num
                        if data_object == []:
                            data_object = next(data)  # Check for empty lines
                        if l == 1:
                            data_object = next(data)
                        people_name = data_object[0]
                        people_email = data_object[1]
                        people_link = str(
                            "https://www.france-bioinformatique.fr/fr/users/" + people_name.replace(" ", "-")
                        ).lower()
                        people_platform = data_object[2]

                        people = ""
                        try:
                            people, created = People.objects.get_or_create(
                                name=people_name,
                                email=people_email,
                                link=people_link,
                                # platform = people_platform,
                            )
                            if created:
                                people.save()

                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this tool: {}\n{}".format(people, str(ex))
                            print(msg)

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_poeple_from_csv_file()
