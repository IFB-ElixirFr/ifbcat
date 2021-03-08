import os
import csv
import json
import urllib3

from django.core.management import BaseCommand
from ifbcat_api.models import Tool
from ifbcat_api.models import Keyword
from ifbcat_api.models import ToolType
from ifbcat_api.models import Team


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    def handle(self, *args, **options):
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)

            first_match_is_not_the_correct_tool = ["Hex", "ARNold", "SuMo"]
            not_imported_tools = first_match_is_not_the_correct_tool
            # do the work
            for data_object in data:
                if data_object == []:
                    continue  # Check for empty lines
                tool_name = data_object[0].strip()

                if tool_name == "SHAMAN: a Shiny Application for Metagenomic ANalysis":
                    tool_name = "SHAMAN"
                if tool_name == "VARiant Annotation and Filtration Tool (VarAFT)":
                    tool_name = "VarAFT"
                if tool_name == "RNAbrowse nouvelle version":
                    tool_name = "RNAbrowse"
                tool_citation = data_object[1]
                tool_logo = data_object[2]
                tool_access_condition = data_object[3]
                tool_description = data_object[5]
                tool_link = data_object[8]
                tool_keywords_bis = data_object[9]
                tool_keywords = tool_keywords_bis.split("\n")
                tool_keywords_list = []
                tool_keyword = ""
                for keyword in tool_keywords:
                    if len(keyword) > 2:
                        try:
                            tool_keyword, created = Keyword.objects.get_or_create(
                                keyword=keyword,
                            )
                            tool_keyword.save()
                            tool_keywords_list.append(tool_keyword)
                            display_format = "\nKeyword, {}, has been saved."
                            print(display_format.format(tool_keyword))
                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this keyword: {}\n{}".format(tool_keyword, str(ex))
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

                if tool_name not in first_match_is_not_the_correct_tool:
                    # Most of the tool infos are gathered first from Bio.tools
                    http = urllib3.PoolManager()
                    req = http.request(
                        'GET', f'https://bio.tools/api/tool/?page=1&q={tool_name}&sort=score&format=json'
                    )
                    response = json.loads(req.data.decode('utf-8'))

                    if response['count'] == 0:
                        print("No match in Bio.tools for '" + tool_name + "'. The tool is not imported.")
                        not_imported_tools.append(tool_name)
                    elif response['count'] > 0:
                        biotoolsID = response['list'][0]['biotoolsID']
                        tool, created = Tool.objects.get_or_create(
                            biotoolsID=biotoolsID,
                            defaults={
                                'name': tool_name,
                                'citations': tool_citation,
                                'logo': tool_logo,
                                'access_condition': tool_access_condition,
                                'description': tool_description,
                                'homepage': tool_link,
                                # should we add downloads to the current model?
                                # downloads=int(tool_downloads),
                                'annual_visits': int(tool_annual_visits),
                                'unique_visits': int(tool_unique_visits),
                            },
                        )
                        print("The '" + tool_name + "' tool is matched with the '" + tool.biotoolsID + "' biotoolsID")
                        # tool.update_information_from_biotool()

                        ## TODO : add check here because the tool_platform is not always a team but sometimes a service, ie ISFinder
                        if tool_platform not in ['ISfinder', 'PRABI-G']:
                            team = Team.objects.get(
                                name=tool_platform,
                            )
                            tool.team.add(team.id)

                        for keyword in tool_keywords_list:
                            tool.keywords.add(keyword)
                        for type in tool_type_list:
                            tool.tool_type.add(type)

                #         tool.save()

                # except Exception as ex:
                #     print(str(ex))
                #     msg = "\n\nSomething went wrong saving this tool: {}\n{}".format(tool, str(ex))
                #     print(msg)
                #     raise ex
        print(not_imported_tools)
