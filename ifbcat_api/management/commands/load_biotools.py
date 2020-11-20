import json
import logging
from json.decoder import JSONDecodeError

import urllib3
from django.core.management import BaseCommand
from tqdm import tqdm

from ifbcat_api.model.misc import Topic, Doi
from ifbcat_api.model.tool.collection import Collection
from ifbcat_api.model.tool.operatingSystem import OperatingSystem
from ifbcat_api.model.tool.tool import Tool
from ifbcat_api.model.tool.toolCredit import ToolCredit, TypeRole
from ifbcat_api.model.tool.toolType import ToolType

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def crawl_tools(self, limit):
        collection_id = 'elixir-fr-sdp-2019'

        # clean tool table
        Tool.objects.all().delete()
        ToolType.objects.all().delete()
        OperatingSystem.objects.all().delete()
        ToolCredit.objects.all().delete()
        Collection.objects.all().delete()

        http = urllib3.PoolManager()
        try:
            req = http.request('GET', f'https://bio.tools/api/tool/?collectionID={collection_id}&page=1&format=json')
            countJson = json.loads(req.data.decode('utf-8'))
            count = int(countJson['count'])
            print(f"{count} available BioTools entries for collection {collection_id}")

            page = 1
            has_next_page = True
            progress_bar = tqdm()
            while has_next_page and (limit == -1 or progress_bar.n < limit):
                req = http.request(
                    'GET', f'https://bio.tools/api/tool/?collectionID={collection_id}&page={page}&format=json'
                )
                try:
                    entry = json.loads(req.data.decode('utf-8'))
                except JSONDecodeError as e:
                    print("Json decode error for " + str(req.data.decode('utf-8')))
                    break

                has_next_page = entry['next'] != None
                # print("Processing page "+str(page)+ " hasNext="+str(has_next_page
                for tool in entry['list']:
                    # print(json.dumps(tool, indent=4))

                    # if 'FR' in tool['collectionID']:
                    # JSONLD url FROM biotools API
                    logger.debug("https://bio.tools/api/" + tool['biotoolsID'] + "?format=jsonld ")

                    # insert in DB tool table here
                    tool_entry, created = Tool.objects.get_or_create(
                        name=tool['name'],
                        description=tool['description'],
                        homepage=tool['homepage'],
                        biotoolsID=tool['biotoolsID'],
                        # publication=tool['publication'],
                        # operating_system = tool['operatingSystem'],
                        # topic = tool['topic'],
                        # link = tool['link'],
                        biotoolsCURIE=tool['biotoolsCURIE'],
                        # software_version = tool['version'],
                        # downloads = tool['download'],
                        tool_license=tool['license'],
                        # language = tool['language'],
                        # otherID = tool['otherID'],
                        maturity=tool['maturity'],
                        # collectionID = tool['collectionID'],
                        # credit = tool['credit'],
                        # elixirPlatform = tool['elixirPlatform'],
                        # elixirNode = tool['elixirNode'],
                        cost=tool['cost'],
                        # accessibility = tool['accessibility'],
                        # function = tool['function'],
                        # relation = tool['relation'],
                    )

                    for destination_field, names in [
                        (tool_entry.tool_type, tool['toolType']),
                        (tool_entry.operating_system, tool['operatingSystem']),
                        (tool_entry.collection, tool['collectionID']),
                    ]:
                        for name in names:
                            instance, _ = destination_field.model.objects.get_or_create(name=name)
                            destination_field.add(instance)

                    # entry for publications DOI
                    for publication in tool['publication']:
                        if 'Primary' in publication['type']:
                            doi = None

                            if publication['doi'] != None:
                                doi = publication['doi']
                            if publication['doi'] == None and publication['pmid'] != None:
                                doi = Doi.get_doi_from_pmid(publication['pmid'])
                                # print('*Get DOI from PMID: ' + str(doi))
                            if publication['doi'] == None and publication['pmcid'] != None:
                                doi = Doi.get_doi_from_pmid(publication['pmcid'])

                            if doi != None:
                                doi_entry, created = Doi.objects.get_or_create(doi=doi)
                                doi_entry.save()
                                tool_entry.primary_publication.add(doi_entry.id)

                    # insert or get DB topic entry table here
                    for topic in tool['topic']:
                        topic_entry, created = Topic.objects.get_or_create(topic=topic['uri'])
                        topic_entry.save()
                        tool_entry.scientific_topics.add(topic_entry.id)

                    tool_entry.save()

                    # entry for toolCredit
                    for credit in tool['credit']:
                        toolCredit_entry, created = ToolCredit.objects.get_or_create(
                            name=credit['name'],
                            email=credit['email'],
                            url=credit['url'],
                            orcidid=credit['orcidid'],
                            gridid=credit['gridid'],
                            typeEntity=credit['typeEntity'],
                            note=credit['note'],
                        )
                        toolCredit_entry.save()
                        tool_entry.tool_credit.add(toolCredit_entry.id)

                        # add typerole entry
                        for type_role in credit['typeRole']:
                            typeRole_entry, created = TypeRole.objects.get_or_create(name=type_role)
                            typeRole_entry.save()
                            toolCredit_entry.type_role.add(typeRole_entry.id)

                    progress_bar.update()
                page += 1
        except urllib3.exceptions.HTTPError as e:
            print("Connection error")
            print(e)
            return None

    def add_arguments(self, parser):
        """
        Arguments for the command line load_biotools
        """
        parser.add_argument(
            '-l', '--limit', help='Number of tools to import (-1 to retrieve all)', type=int, default=-1
        )

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.crawl_tools(options['limit'])
