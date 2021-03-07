import csv
import datetime
import json
import os

import pytz
import unidecode
import urllib3
from django.core.management import BaseCommand
from django.db.transaction import atomic
from django.utils.timezone import make_aware
from tqdm import tqdm

from ifbcat_api.models import Keyword
from ifbcat_api.models import Team
from ifbcat_api.models import Tool


class Command(BaseCommand):
    http = None

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    @atomic
    def handle(self, *args, **options):
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)
            # count number of lines
            data_len = len(list(data))
            data_file.seek(0)
            next(data)
            # do the work

            database_tool_type, created = ToolType.objects.get_or_create(name="Database portal")

            for data_object in tqdm(data, total=data_len):
                if data_object == []:
                    continue  # Check for empty lines
                database_name = data_object[0]
                database_logo = data_object[1]
                database_description = data_object[2]
                database_access_conditions = data_object[3]
                database_citations = data_object[4]
                database_citations = int(database_citations) if database_citations != '' else None
                database_link_data = data_object[5]
                if '\n' in data_object[6]:
                    database_keywords = [x.strip() for x in data_object[6].split("\n")]
                else:
                    database_keywords = [x.strip() for x in data_object[6].split(",")]
                database_keywords_list = []
                for keyword in database_keywords:
                    keyword = keyword.strip()
                    if len(keyword) > 2:

                        try:
                            database_keyword, created = Keyword.objects.get_or_create(
                                keyword=keyword,
                            )
                            database_keyword.save()
                            database_keywords_list.append(database_keyword)
                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(keyword, str(ex))
                            print(msg)

                database_annual_visits = data_object[7].split(" ")[0]
                database_annual_visits = int(database_annual_visits) if database_annual_visits != '' else None
                database_unique_visits = data_object[8].split(" ")[0]
                database_unique_visits = int(database_unique_visits) if database_unique_visits != '' else None
                if data_object[9]:
                    database_last_update = datetime.datetime.strptime(
                        data_object[9], "%d-%m-%Y"
                    )  # .strftime("%Y-%m-%d")
                    database_last_update = make_aware(database_last_update, timezone=pytz.timezone('Europe/Paris'))
                else:
                    database_last_update = None
                database_increase_last_update = data_object[10]
                database_platform = data_object[11]

                database = ""

                try:
                    object_platform = Team.objects.get(
                        name=database_platform,
                    )
                except Team.DoesNotExist:
                    object_platform = None

                try:
                    try:
                        database = Tool.objects.get(name__iexact=database_name)
                        created = False
                        if database.biotoolsID == '':
                            database.biotoolsID = database.name
                    except Tool.DoesNotExist:
                        # clean up anme to get the biotool id
                        biotoolsID = unidecode.unidecode(database_name)
                        if biotoolsID.endswith("2.0"):
                            biotoolsID = biotoolsID[:-3]
                        biotoolsID = biotoolsID.split('(')[0]
                        biotoolsID = biotoolsID.split(':')[0]
                        biotoolsID = biotoolsID.strip()
                        biotoolsID = biotoolsID.replace(' ', '_')
                        if database_name == "Plant data discovery portal":
                            biotoolsID = "Plant_DataDiscovery"
                        if database_name == "Wheat@URGI":
                            biotoolsID = "WheatIS"

                        # try to get it from the db
                        try:
                            database = Tool.objects.get(biotoolsID__iexact=biotoolsID)
                        except Tool.DoesNotExist:
                            # not found, so create a new entry, and bypass autofill
                            database = Tool.objects.create(
                                name=database_name,
                            )
                            biotool_db = self.get_from_biotools(biotoolsID)
                            if biotool_db.get("detail", None) != "Not found.":
                                database.biotoolsID = biotoolsID
                                database.update_information_from_json(biotool_db)
                    if created and database.name is '':
                        Tool.objects.filter(pk=database.pk).update(
                            **{
                                'name': database_name,
                                'logo': database_logo,
                                'description': database_description,
                                'access_condition': database_access_conditions,
                                'citations': database_citations,
                                'homepage': database_link_data,
                                'annual_visits': database_annual_visits,
                                'unique_visits': database_unique_visits,
                                'last_update': database_last_update,
                                # 'increase_last_update' is not in Tool model.
                                # Maybe we could create a Database model inheriting from Tool
                                # with this additionnal field?
                                # 'increase_last_update': database_increase_last_update
                            }
                        )

                    database.refresh_from_db()
                    if database.name == '':
                        raise ValueError(f'We should not end up with an empty name for {database_name}')
                except Exception as e:
                    print(data_object)
                    raise e

                if object_platform:
                    database.team.add(object_platform)

                display_format = "\nDatabase, {}, has been saved."
                # print(display_format.format(database))
                for keyword in database_keywords_list:
                    database.keywords.add(keyword)

                database.tool_type.add(database_tool_type)

                # biotoolsCURIE and biotoolsID are missing for validation
                # database.full_clean()
                database.save()

    def get_from_biotools(self, biotoolsID):
        key = None
        cache_dir = os.environ.get('CACHE_DIR', None)
        if cache_dir is not None:
            cache_dir = os.path.join(cache_dir, 'biotools')
            os.makedirs(cache_dir, exist_ok=True)
            key = f'{biotoolsID}.json'
            try:
                with open(os.path.join(cache_dir, key)) as f:
                    response = json.load(f)
                return response
            except FileNotFoundError:
                pass

        if self.http is None:
            self.http = urllib3.PoolManager()
        req = self.http.request('GET', f'https://bio.tools/api/{biotoolsID}?format=json')
        response = json.loads(req.data.decode('utf-8'))

        if key is not None:
            with open(os.path.join(cache_dir, key), 'w') as f:
                json.dump(response, f)
        return response
