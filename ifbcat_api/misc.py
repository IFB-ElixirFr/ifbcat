import json
import os

import requests


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
