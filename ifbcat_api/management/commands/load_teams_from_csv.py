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
from ifbcat_api.model.team import Team

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the CSV file containing columns named after Team model.",
            default="import_data/manual_curation/teams.csv",
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
                    t, created = Team.objects.update_or_create(
                        name=data_object[0],
                        defaults={
                            'description': data_object[1],
                            'homepage': data_object[2],
                            'logo_url': data_object[3],
                            # 'fields' : data_object[4],
                            # 'keywords' : data_object[5],
                            # 'expertise' : data_object[6],
                            # 'linkCovid19' : data_object[7],
                            # 'leader' : data_object[8],
                            # 'deputies' : data_object[9],
                            # 'scientificLeaders' : data_object[10],
                            # 'technicalLeaders' : data_object[11],
                            # 'members' : data_object[12],
                            # 'maintainers' : data_object[13],
                            # 'unitId' : data_object[14],
                            'address': data_object[15],
                            'city': data_object[16],
                            'country': data_object[17],
                            #'orgid' : data_object[18],
                            # 'communities' : data_object[19],
                            # 'projects' : data_object[20],
                            # 'fundedBy' : data_object[21],
                            # 'publications' : data_object[22],
                            # 'certifications' : data_object[23],
                            # 'affiliatedWith' : data_object[24]
                        },
                    )
                    t.save()

                except Exception as e:
                    logger.error(t)
                    print('error' + data_object[0])
                    raise e
