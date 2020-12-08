import csv
import datetime
import logging
import os
import zipfile
import pandas as pd

import pytz
from django.core.management import BaseCommand
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model
import urllib.request
import json

from tqdm import tqdm

from ifbcat_api.model.event import *
from ifbcat_api.model.organisation import Organisation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the CSV file containing one 'orgid' column.",
            default="import_data/manual_curation/organisations.csv",
        )

    def handle(self, *args, **options):
        with open(options["file"], encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            data_len = len(list(data))
            data_file.seek(0)
            # skip first line as there is always a header
            next(data)
            # do the work
            for data_object in tqdm(data, total=data_len):
                if data_object == []:
                    continue  # Check for empty lines
                try:
                    print(data_object[0])
                    o, created = Organisation.objects.update_or_create(
                        name=data_object[0],
                        defaults={
                            'description': data_object[1],
                            'homepage': data_object[2],
                            # M2M:
                            #'fields': data_object[3],
                            'city': data_object[4],
                            'logo_url': data_object[5],
                        },
                    )
                    o.save()

                except Exception as e:
                    logger.error(o)
                    print('error' + name)
                    raise e
