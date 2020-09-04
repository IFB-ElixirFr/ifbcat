import os
import csv
from django.core.management import BaseCommand
from database.models import Tool
from database.models import Keyword
from database.models import ToolType
from database.models import Platform
from catalogue.settings import BASE_DIR


class Command(BaseCommand):
    def import_tools_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, 'import_data', 'resources/csv_file')
        Tool.objects.all().delete()
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "tools.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    data = csv.reader(data_file)
                    # skip first line as there is always a header
                    next(data)
                    # do the work
                    for data_object in data:
                        if data_object == []:
                            continue  # Check for empty lines
                        tool_name = data_object[0]
                        print(tool_name)
                        tool_citation = data_object[1]
                        tool_logo = data_object[2]
                        tool_access_condition = data_object[3]
                        tool_description = data_object[5]
                        tool_link = data_object[8]
                        tool_keywords_bis = data_object[9]
                        tool_keywords = tool_keywords_bis.split(",")
                        tool_keywords_list = []
                        tool_keyword = ""
                        for keyword in tool_keywords:
                            if len(keyword) > 2:

                                try:

                                    tool_keyword, created = Keyword.objects.get_or_create(
                                        name=keyword,
                                    )
                                    tool_keyword.save()
                                    tool_keywords_list.append(tool_keyword)
                                    display_format = "\nKeyword, {}, has been saved."
                                    print(display_format.format(tool_keyword))
                                except Exception as ex:
                                    print(str(ex))
                                    msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(
                                        tool_keyword, str(ex)
                                    )
                                    print(msg)

                        tool_types_bis = data_object[13]
                        tool_types = tool_types_bis.split(",")
                        tool_type_list = []
                        tool_type = ""
                        for type in tool_types:
                            if len(type) > 2:

                                try:

                                    tool_type, created = ToolType.objects.get_or_create(
                                        name=type,
                                    )
                                    tool_type.save()
                                    tool_type_list.append(tool_type)
                                    display_format = "\nType, {}, has been saved."
                                    print(display_format.format(tool_type))
                                except Exception as ex:
                                    print(str(ex))
                                    msg = "\n\nSomething went wrong saving this type: {}\n{}".format(tool_type, str(ex))
                                    print(msg)

                        tool_downloads = data_object[14] or 0
                        tool_annual_visits = data_object[16].split(" ")[0] or 0
                        tool_unique_visits = data_object[17].split(" ")[0] or 0
                        tool_platform = data_object[19]
                        print(tool_platform)

                        tool = ""
                        object_platform = Platform.objects.get(
                            name=tool_platform,
                        )
                        print(object_platform.id)
                        try:
                            tool, created = Tool.objects.get_or_create(
                                name=tool_name,
                                citations=tool_citation,
                                logo=tool_logo,
                                access_condition=tool_access_condition,
                                description=tool_description,
                                link=tool_link,
                                downloads=int(tool_downloads),
                                annual_visits=int(tool_annual_visits),
                                unique_visits=int(tool_unique_visits),
                            )
                            print(created)
                            tool.platform.add(object_platform.id)
                            if created:
                                tool.save()

                                display_format = "\nTool, {}, has been saved."
                                print(display_format.format(tool))
                                for keyword in tool_keywords_list:
                                    tool.keywords.add(keyword)
                                for type in tool_type_list:
                                    tool.tool_type.add(type)

                                tool.save()

                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this tool: {}\n{}".format(tool, str(ex))
                            print(msg)
                            raise ex

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_tools_from_csv_file()
