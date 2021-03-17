import csv
import json
import logging
import os
from typing import Optional

import pylev
import urllib3
from django.core.management import BaseCommand

from ifbcat_api.models import Keyword
from ifbcat_api.models import Team
from ifbcat_api.models import Tool
from ifbcat_api.models import ToolType

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    http = None

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the CSV source file")

    def handle(self, *args, **options):
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            # skip first line as there is always a header
            next(data)

            first_match_is_not_the_correct_tool = ["Hex", "ARNold", "SuMo"]
            match_too_broad = []
            no_match = []
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
                if tool_name == "Regulatory Sequence Analysis Tools (RSAT)":
                    tool_name = "rsat"
                tool_citation_count = data_object[1]
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
                            tool_keywords_list.append(tool_keyword)
                            logger.debug(f"Keyword, {tool_keyword}, has been saved.")
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
                            logger.debug(f"Type, {tool_keyword}, has been saved.")
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
                    response = self.get_from_biotools(tool_name)

                    if response['count'] == 0:
                        logger.debug("No match in Bio.tools for '" + tool_name + "'. The tool is not imported.")
                        no_match.append(tool_name)
                        continue
                    tool_item = self.get_best_match(response, tool_name)
                    if tool_item is None:
                        tool_item = self.get_best_match(response, tool_name, max_edition_percentage=None)
                        logger.debug(
                            "The best match for '"
                            + tool_name
                            + "' is '"
                            + tool_item['biotoolsID']
                            + "' but is too different, we do not import it."
                        )
                        match_too_broad.append(tool_name)
                        continue
                    tool = Tool.objects.filter(biotoolsID__iexact=tool_item['biotoolsID']).first()
                    if tool is None:
                        tool = Tool.objects.filter(name__iexact=tool_item['name']).first()
                        if tool is not None and (tool.biotoolsID is None or tool.biotoolsID == ""):
                            tool.biotoolsID = tool_item['biotoolsID']
                            tool.logo = tool_logo
                            tool.access_condition = tool_access_condition
                            tool.annual_visits = int(tool_annual_visits)
                            tool.unique_visits = int(tool_unique_visits)
                            tool.save()
                            tool.update_information_from_json(tool_item)
                    if tool is None:
                        tool = Tool.objects.create(
                            name=tool_item['biotoolsID'],
                        )
                        tool.biotoolsID = tool_item['biotoolsID']
                        tool.logo = tool_logo
                        tool.access_condition = tool_access_condition
                        tool.annual_visits = int(tool_annual_visits)
                        tool.unique_visits = int(tool_unique_visits)
                        tool.update_information_from_json(tool_item)
                    logger.debug(f"The '{tool_name}' tool is matched with the '{tool.biotoolsID}' biotoolsID")

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

        logger.warning(f"Not imported tools: {', '.join(no_match + match_too_broad)}")
        logger.warning("Too broad:\n\t\t" + '\n\t\t'.join(match_too_broad))
        logger.warning("No match:\n\t\t" + '\n\t\t'.join(no_match))

    def get_from_biotools(self, tool_name):
        key = None
        cache_dir = os.environ.get('CACHE_DIR', None)
        if cache_dir is not None:
            cache_dir = os.path.join(cache_dir, 'biotools')
            os.makedirs(cache_dir, exist_ok=True)
            key = f'q.{tool_name.replace(" ", "").replace("/", "").replace(":", "")}.json'
            try:
                with open(os.path.join(cache_dir, key)) as f:
                    response = json.load(f)
                return response
            except FileNotFoundError:
                pass

        if self.http is None:
            self.http = urllib3.PoolManager()
        req = self.http.request('GET', f'https://bio.tools/api/tool/?page=1&q={tool_name}&sort=score&format=json')
        response = json.loads(req.data.decode('utf-8'))

        if key is not None:
            with open(os.path.join(cache_dir, key), 'w') as f:
                json.dump(response, f)
        return response

    @staticmethod
    def normalize(string: str):
        return string.replace("-", "").upper()

    def get_best_match(self, response, tool_name, max_edition_percentage: Optional[float] = 0.1):
        # biotoolsID = response['list'][0]['biotoolsID']
        biotools_item = None
        normalized_name = self.normalize(tool_name)
        min_edit = len(tool_name) * 10000
        for item in response['list']:
            choice_edit = pylev.levenshtein(normalized_name, self.normalize(item['biotoolsID']))
            if choice_edit < min_edit:
                min_edit = choice_edit
                biotools_item = item
            choice_edit = pylev.levenshtein(normalized_name, self.normalize(item['name']))
            if choice_edit < min_edit:
                min_edit = choice_edit
                biotools_item = item
        if max_edition_percentage is not None and min_edit > len(tool_name) * max_edition_percentage:
            return None
        return biotools_item
