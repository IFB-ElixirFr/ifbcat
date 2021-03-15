import csv
import json
import logging
import os
import re

import urllib3
from django.core.management import BaseCommand
from tqdm import tqdm

from ifbcat_api.model.organisation import Organisation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    http = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the CSV file containing one 'orgid' column.",
            default="import_data/manual_curation/mapping_organisations.csv",
        )

    def handle(self, *args, **options):
        grid = re.compile('grid.\d+.*')
        with open(os.path.join(options["file"]), encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            data_len = len(list(data))
            data_file.seek(0)

            # skip first line as there is always a header
            next(data)
            # do the work
            for data_object in tqdm(data, total=data_len):
                drupal_name = data_object[0]
                ifbcat_name = data_object[1]
                orgid = data_object[2]
                if grid.match(orgid):
                    response = self.get_from_grid_ac(orgid)

                    if response['institute']['acronyms']:
                        name = response['institute']['acronyms'][0]
                    else:
                        name = response['institute']['name']

                    description = response['institute']['name']
                    homepage = response['institute']['links'][0]
                    orgid = response['institute']['id']
                    # fields = Nothing available in Grid
                    city = response['institute']['addresses'][0]['city']
                    # logo_url = p = Nothing available in Grid

                    try:
                        o, created = Organisation.objects.update_or_create(
                            name=name,
                            defaults={
                                'orgid': orgid,
                                'description': description,
                                'homepage': homepage,
                                'city': city,
                            },
                        )
                        o.save()

                    except Exception as e:
                        logger.error(o)
                        print('error' + name)
                        raise e

    def get_from_grid_ac(self, orgid):
        key = None
        cache_dir = os.environ.get('CACHE_DIR', None)
        if cache_dir is not None:
            cache_dir = os.path.join(cache_dir, 'grid.ac')
            os.makedirs(cache_dir, exist_ok=True)
            key = f'{orgid}.json'
            try:
                with open(os.path.join(cache_dir, key)) as f:
                    response = json.load(f)
                return response
            except FileNotFoundError:
                pass

        if self.http is None:
            self.http = urllib3.PoolManager()
        req = self.http.request('GET', f'https://www.grid.ac/institutes/{orgid}?format=json')
        response = json.loads(req.data.decode('utf-8'))

        if key is not None:
            with open(os.path.join(cache_dir, key), 'w') as f:
                json.dump(response, f)
        return response
