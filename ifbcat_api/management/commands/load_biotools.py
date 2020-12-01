import json
import logging
from json.decoder import JSONDecodeError

import urllib3
from django.core.management import BaseCommand
from tqdm import tqdm

from ifbcat_api.model.tool.tool import Tool

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def crawl_tools(self, limit, collection_id):
        # clean tool table
        # Tool.objects.all().delete()
        # ToolType.objects.all().delete()
        # OperatingSystem.objects.all().delete()
        # ToolCredit.objects.all().delete()
        # Collection.objects.all().delete()

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

                has_next_page = entry['next'] is not None
                for tool in entry['list']:
                    logger.warning("https://bio.tools/api/" + tool['biotoolsID'] + "?format=jsonld ")
                    tool_entry, created = Tool.objects.get_or_create(
                        name=tool['name'],
                        # biotoolsID=tool['biotoolsID'],
                    )
                    tool_entry.update_information_from_json(tool)

                    progress_bar.update()
                page += 1
        except urllib3.exceptions.HTTPError as e:
            logger.error("Connection error")
            logger.error(e)

    def add_arguments(self, parser):
        """
        Arguments for the command line load_biotools
        """
        parser.add_argument(
            '-l', '--limit', help='Number of tools to import (-1 to retrieve all)', type=int, default=-1
        )
        parser.add_argument(
            '-c',
            '--collection_id',
            help='Number of tools to import (-1 to retrieve all)',
            type=str,
            default='elixir-fr-sdp-2019',
        )

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.crawl_tools(limit=options['limit'], collection_id=options['collection_id'])
