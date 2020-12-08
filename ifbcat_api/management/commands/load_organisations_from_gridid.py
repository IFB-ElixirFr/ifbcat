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
            default="import_data/manual_curation/mapping_organisations.csv",
        )

    def handle(self, *args, **options):
        df = pd.read_csv(options["file"], sep=",")
        print(df)

        url = 'https://s3-eu-west-1.amazonaws.com/pstorage-digitalscience-874864551/25039403/grid20201006.zip'
        local_grid_archive = os.path.basename(url)
        if not os.path.isfile(local_grid_archive):
            urllib.request.urlretrieve(url, local_grid_archive)  # , file=local_grid_archive)

        extracted_grid_dir = "/tmp/ifbcat_grid_archive"
        with zipfile.ZipFile(local_grid_archive, "r") as zip_ref:
            zip_ref.extractall(extracted_grid_dir)

        with open(extracted_grid_dir + "/grid.json") as json_file:
            data = json.load(json_file)
            for p in data['institutes']:
                # try:
                #     if 'INRA' in p['acronyms']:
                #         print(p)
                # except:
                #     "No acronym for this institute"
                if p['id'] in df['orgid'].dropna().tolist():
                    try:
                        print(p['acronyms'])
                        if not p['acronyms']:
                            name = p['name']
                        else:
                            name = p['acronyms'][0]

                        description = p['name']
                        homepage = p['links'][0]
                        orgid = p['id']
                        # fields = Nothing available in Grid
                        city = p['addresses'][0]['city']
                        # logo_url = p = Nothing available in Grid

                    except Exception as e:
                        logger.error(p)
                        raise e

                    try:
                        o, created = Organisation.objects.update_or_create(
                            name=name,
                            defaults={
                                'description': description,
                                'homepage': homepage,
                                'orgid': orgid,
                                'city': city,
                            },
                        )
                        o.save()
                        print('save ' + name)

                    except Exception as e:
                        logger.error(o)
                        print('error' + name)
                        raise e
