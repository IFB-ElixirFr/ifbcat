import csv
import datetime
import logging
import os
import json
import urllib3
import re
from tqdm import tqdm

import pytz
from django.core.management import BaseCommand
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model

from ifbcat_api.model.event import *
from ifbcat_api.model.organisation import Organisation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
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
                    http = urllib3.PoolManager()
                    req = http.request('GET', f'https://www.grid.ac/institutes/{orgid}?format=json')
                    response = json.loads(req.data.decode('utf-8'))

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
