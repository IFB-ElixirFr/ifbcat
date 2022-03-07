import json
import logging
from json.decoder import JSONDecodeError

import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from urllib3.exceptions import MaxRetryError
from django.conf import settings

from ifbcat_api import permissions
from ifbcat_api.model.misc import Topic, Doi, Keyword, Licence
from ifbcat_api.model.tool.collection import Collection
from ifbcat_api.model.tool.operatingSystem import OperatingSystem
from ifbcat_api.model.tool.toolCredit import ToolCredit, TypeRole
from ifbcat_api.model.tool.toolType import ToolType

logger = logging.getLogger(__name__)


class Database(models.Model):
    class Meta:
        ordering = ('name', 'fairsharingID')

    name = models.CharField(
        unique=True,
        blank=False,
        null=False,
        max_length=100,
    )
    description = models.TextField(blank=True)
    homepage = models.URLField(max_length=512, help_text="Homepage of the tool.", blank=True, null=True)
    fairsharingID = models.CharField(blank=False, null=False, max_length=100)
    tool_type = models.ManyToManyField(ToolType, blank=True)
    # Use edam topics from Topic table
    scientific_topics = models.ManyToManyField(
        Topic,
        blank=True,
    )
    operating_system = models.ManyToManyField(
        OperatingSystem,
        blank=True,
    )
    tool_credit = models.ManyToManyField(ToolCredit, blank=True)
    tool_licence = models.ForeignKey(
        Licence, blank=True, null=True, on_delete=models.SET_NULL, help_text="Licence of the tool."
    )
    documentation = models.URLField(
        max_length=512, null=True, blank=True, help_text="Link toward general documentation of the tool"
    )
    # add operation/function here
    # Primary publication DOI storedin DOI table
    primary_publication = models.ManyToManyField(
        Doi,
        related_name='database_doi',
        blank=True,
        help_text="Publication(s) that describe the tool as a whole.",
    )
    collection = models.ManyToManyField(Collection, blank=True)
    # software_version = models.CharField(max_length=200, blank=True, null=True)
    citations = models.CharField(max_length=1000, blank=True, null=True)
    link = models.CharField(max_length=1000, blank=True, null=True, help_text="Link of the tool toward FAIRsharing.")
    # keywords = models.ManyToManyField(Keyword, blank=True)
    downloads = models.CharField(max_length=1000, blank=True, null=True)
    annual_visits = models.IntegerField(blank=True, null=True)
    unique_visits = models.IntegerField(blank=True, null=True)

    # added fields
    maturity = models.CharField(max_length=1000, null=True, blank=True)
    # collectionID = models.CharField(max_length=1000, null=True, blank=True)
    # credit = models.TextField(null=True, blank=True)
    cost = models.CharField(max_length=1000, null=True, blank=True)
    # accessibility = models.CharField(max_length=1000, null=True, blank=True)

    # TODO: Should be useful ?
    input_data = models.CharField(max_length=1000, blank=True, null=True)
    output_data = models.CharField(max_length=1000, blank=True, null=True)

    # metadata
    addition_date = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.UserCanAddNew
            | permissions.UserCanDeleteIfNotUsed
            | permissions.SuperuserCanDelete,
            IsAuthenticatedOrReadOnly,
        )

    def get_jwt_with_credentials(self, username, password):
        url = "https://api.fairsharing.org/users/sign_in"
        payload = dict(user=dict(login=username, password=password))
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

        # Get the JWT from the response.text to use in the next part.
        data = response.json()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': "Bearer {0}".format(data['jwt']),
        }
        return headers

    def update_information_from_fairsharing(self):
        try:
            url = f"https://api.fairsharing.org/search/fairsharing_records?q={self.fairsharingID}"
            response = requests.request(
                "POST",
                url,
                headers=self.get_jwt_with_credentials(
                    settings.FAIRSHARING_LOGIN,
                    settings.FAIRSHARING_PASSWORD,
                ),
            )
            entries = response.json()
        except (JSONDecodeError, MaxRetryError) as e:
            logger.error(f"Error with {self.fairsharingID}: {e}")
            return
        if not entries['data']:
            logger.error(f"We do not have data for: {self.fairsharingID}")
            return
        for entry in entries['data']:
            if entry['attributes']['abbreviation'].casefold() == self.fairsharingID.casefold():
                self.update_information_from_json(entry)

    def update_information_from_json(self, tool: dict):
        # insert in DB tool table here
        self.name = tool['attributes']['name'][24:]
        self.description = tool['attributes']['description'][35:]
        # self.homepage = tool['homepage']
        self.fairsharingID = tool['attributes']['abbreviation']
        self.link = tool['attributes']['url']
        # software_version = tool['version']
        # TODO : We got many licences which one should we take?
        # self.tool_license = tool['attributes']['licence-links'][0]['licence-name']
        self.last_update = tool['attributes']['updated-at']
        self.save()

        # entry for publications DOI
        for publication in tool['attributes']['publications']:
            doi = None
            if publication['doi'] != None:
                doi = publication['doi']
            if publication['doi'] == None and publication['pubmed_id'] != None:
                doi = Doi.get_doi_from_pmid(publication['pubmed_id'])
                # print('*Get DOI from PUBMED_ID: ' + str(doi))
            if publication['doi'] == None and publication['pubmed_id'] != None:
                doi = Doi.get_doi_from_pmid(publication['pubmed_id'])
            if doi != None:
                doi_entry, created = Doi.objects.get_or_create(doi=doi)
                doi_entry.save()
                self.primary_publication.add(doi_entry.id)


@receiver(post_save, sender=Database)
def update_information_from_fairsharing(sender, instance, created, **kwargs):
    if created and instance.fairsharingID is not None and instance.fairsharingID != "":
        instance.update_information_from_fairsharing()
