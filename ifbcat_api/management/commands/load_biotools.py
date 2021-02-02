import json
import logging
import os
from json.decoder import JSONDecodeError

import urllib3
from django.core.management import BaseCommand
from tqdm import tqdm

from ifbcat_api.model.tool.tool import Tool

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    http = None

    def crawl_tools(self, limit, collection_id, cache_dir=None):
        # clean tool table
        # Tool.objects.all().delete()
        # ToolType.objects.all().delete()
        # OperatingSystem.objects.all().delete()
        # ToolCredit.objects.all().delete()
        # Collection.objects.all().delete()

        try:
            resp = self.get_from_biotools(collection_id=collection_id, page=1, cache_dir=cache_dir)
            count = int(resp['count'])
            print(f"{count} available BioTools entries for collection {collection_id}")

            page = 1
            has_next_page = True
            progress_bar = tqdm()
            while has_next_page and (limit == -1 or progress_bar.n < limit):
                try:
                    entry = self.get_from_biotools(collection_id=collection_id, page=page, cache_dir=cache_dir)
                except JSONDecodeError as e:
                    logging.error("Json decode error")
                    break

                has_next_page = entry['next'] is not None
                for tool in entry['list']:
                    logger.info("https://bio.tools/api/" + tool['biotoolsID'] + "?format=jsonld ")
                    tool_entry = Tool.objects.filter(biotoolsID__iexact=tool['biotoolsID']).first()
                    if tool_entry is None:
                        tool_entry = Tool.objects.filter(name__iexact=tool['name']).first()
                        if tool_entry is not None and (tool_entry.biotoolsID is None or tool_entry.biotoolsID == ""):
                            tool_entry.biotoolsID = tool['biotoolsID']
                            tool_entry.save()
                            tool_entry.update_information_from_json(tool)
                    if tool_entry is None:
                        tool_entry = Tool.objects.create(
                            biotoolsID=tool['biotoolsID'],
                        )
                        tool_entry.update_information_from_json(tool)

                    progress_bar.update()
                page += 1
        except urllib3.exceptions.HTTPError as e:
            logger.error("Connection error")
            logger.error(e)

    def get_from_biotools(self, collection_id, page, cache_dir: str):
        key = None
        if cache_dir is not None:
            key = f'{collection_id}.{page}.json'
            try:
                with open(os.path.join(cache_dir, key)) as f:
                    response = json.load(f)
                return response
            except FileNotFoundError:
                pass

        if self.http is None:
            self.http = urllib3.PoolManager()
        req = self.http.request(
            'GET', f'https://bio.tools/api/tool/?collectionID={collection_id}&page={page}&format=json'
        )
        response = json.loads(req.data.decode('utf-8'))

        if key is not None:
            with open(os.path.join(cache_dir, key), 'w') as f:
                json.dump(response, f)
        return response

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
        parser.add_argument(
            '--cache_dir',
            help='Folder where are/will be stored the raw json downloaded',
            type=str,
            default=None,
        )

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.crawl_tools(limit=options['limit'], collection_id=options['collection_id'], cache_dir=options['cache_dir'])
