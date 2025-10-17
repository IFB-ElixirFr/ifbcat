import json
import os

import pylev
import requests
from django.conf import settings
from django.db.models import ManyToManyRel, ManyToOneRel
from opencage.geocoder import OpenCageGeocode
from rest_framework import serializers


class BibliographicalEntryNotFound(Exception):
    def __init__(self, entry_id: str, status_code: int = None, msg: Exception = None):
        self.entry_id = entry_id
        _msg = f"{entry_id} not found."
        if status_code is not None:
            _msg += f" status code: {status_code})."
        if msg is not None:
            _msg += f" error message: {msg}"
        super().__init__(msg)


def get_doi_info(doi: str) -> dict:
    """
    Retrieve information about a publication from DOI web services

    :authors https://gitlab.pasteur.fr/ippidb/ippidb-web/-/blob/master/ippisite/ippidb/ws.py

    :param doi: DOI
    :type doi: str
    :return: publication metadata (title, journal name, publication year, authors list).
    :rtype: dict
    """
    cache_dir = os.environ.get('CACHE_DIR', None)
    key = None
    if cache_dir is not None:
        cache_dir = os.path.join(cache_dir, 'doi')
        os.makedirs(cache_dir, exist_ok=True)
        key = f'{doi.replace("/", "-")}.json'
        try:
            with open(os.path.join(cache_dir, key)) as f:
                response = json.load(f)
            return response
        except FileNotFoundError:
            pass
    resp = requests.get(
        "http://dx.doi.org/%s" % doi,
        headers={"Accept": "application/vnd.citationstyles.csl+json"},
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as he:
        if resp.status_code == 404:
            raise BibliographicalEntryNotFound(doi, resp.status_code, he) from he
        else:
            raise he
    json_data = resp.json()
    title = json_data["title"]
    journal_name = json_data.get("container-title", json_data.get("original-title", None))
    biblio_year = 0
    try:
        if "journal-issue" in json_data and "published-print" in json_data["journal-issue"]:
            biblio_year = json_data["journal-issue"]["published-print"]["date-parts"][0][0]
        elif "published-print" in json_data:
            biblio_year = json_data["published-print"]["date-parts"][0][0]
        elif "issued" in json_data:
            biblio_year = json_data["issued"]["date-parts"][0][0]
        else:
            biblio_year = json_data["published-online"]["date-parts"][0][0]
    except KeyError as e:
        print("http://dx.doi.org/%s" % doi)
        print(json_data)
        raise e
    authors_list = []
    for author_data in json_data.get("author", []):
        try:
            if "family" in author_data:
                authors_list.append("%s %s" % (author_data["family"], author_data.get("given", "")))
            else:
                authors_list.append(author_data["name"])
        except KeyError as e:
            print("http://dx.doi.org/%s" % doi)
            print(json_data)
            raise e
    authors = ", ".join(authors_list)
    response = {
        "title": title,
        "journal_name": journal_name,
        "biblio_year": biblio_year,
        "authors_list": authors,
    }
    if key is not None:
        with open(os.path.join(cache_dir, key), 'w') as f:
            json.dump(response, f)
    return response


def get_usage_in_related_field(queryset):
    attrs = []
    for model_field in queryset.model._meta.get_fields():
        if isinstance(model_field, ManyToManyRel) or isinstance(model_field, ManyToOneRel):
            attr_name = model_field.related_name or (model_field.name + "_set")
            reverse_name = model_field.remote_field.name
            attrs.append((model_field, attr_name, reverse_name))
    return attrs


def inline_serializer_factory(klass, fields=None, lookup_field='pk', url=True):
    if fields is None:
        serialized_fields = ['id', 'name']
    else:
        serialized_fields = list(fields)
    name = klass._meta.label.split(".")[-1]
    if url:

        class _tmp(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = klass
                fields = serialized_fields + ['url']

            url = serializers.HyperlinkedIdentityField(
                read_only=True,
                view_name=f'{name.lower()}-detail',
                lookup_field=lookup_field,
            )

    else:

        class _tmp(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = klass
                fields = serialized_fields

    _tmp.__name__ = name + "InlineSerializer"
    return _tmp


def guess_coordinate_from_address(address):
    geocoder = OpenCageGeocode(settings.OPEN_CAGE_GEO_CODE_KEY)
    results = geocoder.geocode(address)
    if len(results) == 0:
        return None
    result = min(results, key=lambda x: pylev.levenshtein(x['formatted'], address))
    print(result['annotations']['OSM']['url'])
    return result['geometry']


def get_file_size_from_url(url) -> int:
    """
    Return the size of a file in KB.
    """
    response = requests.get(url)
    response.raise_for_status()
    current_size = len(response.content) // 1024
    return current_size
