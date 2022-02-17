import json
import logging
from json.decoder import JSONDecodeError

import urllib3
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from urllib3.exceptions import MaxRetryError

from ifbcat_api import permissions
from ifbcat_api.model.misc import Topic, Doi, Keyword, Licence
from ifbcat_api.model.tool.collection import Collection
from ifbcat_api.model.tool.operatingSystem import OperatingSystem
from ifbcat_api.model.tool.toolCredit import ToolCredit, TypeRole
from ifbcat_api.model.tool.toolType import ToolType

logger = logging.getLogger(__name__)


class Tool(models.Model):
    class Meta:
        ordering = ('name', 'biotoolsID')

    name = models.CharField(
        unique=True,
        blank=False,
        null=False,
        max_length=100,
    )
    description = models.TextField(blank=True)
    homepage = models.URLField(max_length=512, help_text="Homepage of the tool.", blank=True, null=True)
    biotoolsID = models.CharField(blank=False, null=False, max_length=100)
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
        related_name='tools',
        blank=True,
        help_text="Publication(s) that describe the tool as a whole.",
    )
    collection = models.ManyToManyField(Collection, blank=True)
    biotoolsCURIE = models.CharField(blank=False, null=False, max_length=109)  # because of biotools: prefix

    # software_version = models.CharField(max_length=200, blank=True, null=True)

    citations = models.CharField(max_length=1000, blank=True, null=True)

    # link = models.CharField(max_length=1000, blank=True, null=True)
    # keywords = models.ManyToManyField(Keyword, blank=True)
    # operating_system = models.CharField(max_length=50, blank=True, null=True, choices=OPERATING_SYSTEM_CHOICES)
    # topic = models.CharField(max_length=1000, blank=True, null=True)
    downloads = models.CharField(max_length=1000, blank=True, null=True)
    annual_visits = models.IntegerField(blank=True, null=True)
    unique_visits = models.IntegerField(blank=True, null=True)

    # many_to_many
    # platform = models.ManyToManyField(Platform, blank=True)
    # team = models.ManyToManyField(
    #     Team,
    #     blank=True,
    #     related_name='ToolsTeams',
    #     help_text="Team developping the tool.",
    # )
    # language = models.ManyToManyField(Language, blank=True)

    # elixir_platform = models.ManyToManyField(ElixirPlatform, blank=True)
    # elixir_node = models.ManyToManyField(ElixirNode, blank=True)
    # accessibility = models.ManyToManyField(Accessibility, blank=True)

    # link = models.ManyToManyField(Link, blank=True)

    # added fields
    # language = models.CharField(max_length=1000, null=True, blank=True)
    # otherID = models.CharField(max_length=1000, null=True, blank=True)
    maturity = models.CharField(max_length=1000, null=True, blank=True)

    # collectionID = models.CharField(max_length=1000, null=True, blank=True)
    # credit = models.TextField(null=True, blank=True)
    # elixirNode = models.CharField(max_length=1000, null=True, blank=True)
    # elixirPlatform = models.CharField(max_length=1000, null=True, blank=True)
    cost = models.CharField(max_length=1000, null=True, blank=True)
    # accessibility = models.CharField(max_length=1000, null=True, blank=True)
    # function = models.TextField(null=True, blank=True)
    # relation = models.CharField(max_length=1000, null=True, blank=True)

    # to remove ?
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

    def update_information_from_biotool(self):
        try:
            http = urllib3.PoolManager()
            req = http.request('GET', f'https://bio.tools/api/{self.biotoolsID}?format=json')
            entry = json.loads(req.data.decode('utf-8'))
        except (JSONDecodeError, MaxRetryError) as e:
            logger.error(f"Error with {self.biotoolsID}: {e}")
            return
        if entry.get('detail', None) is not None:
            logger.error(f"Error with {self.biotoolsID}: {entry['detail']}")
            return
        self.update_information_from_json(entry)

    def update_information_from_json(self, tool: dict):
        # insert in DB tool table here
        self.name = tool['name']
        self.description = tool['description']
        self.homepage = tool['homepage']
        self.biotoolsID = tool['biotoolsID']
        # link = tool['link']
        self.biotoolsCURIE = tool['biotoolsCURIE']
        # software_version = tool['version']
        # downloads = tool['download']
        self.tool_license = tool['license']
        for doc in tool['documentation']:
            if 'General' in doc['type'] or 'User manual' in doc['type']:
                self.documentation = doc['url']
                break
            elif 'API documentation' in doc['type'] or 'FAQ' in doc['type']:
                self.documentation = doc['url']
                break
            else:
                self.documentation = None
        # language = tool['language']
        # otherID = tool['otherID']
        self.maturity = tool['maturity']
        # elixirPlatform = tool['elixirPlatform']
        # elixirNode = tool['elixirNode']
        self.cost = tool['cost']
        # accessibility = tool['accessibility']
        # function = tool['function']
        # relation = tool['relation']
        self.last_update = tool['lastUpdate']

        self.save()

        for destination_field, names in [
            (self.tool_type, tool['toolType']),
            (self.operating_system, tool['operatingSystem']),
            (self.collection, tool['collectionID']),
        ]:
            for name in names:
                instance, _ = destination_field.model.objects.get_or_create(name=name)
                destination_field.add(instance)

        # entry for publications DOI
        for publication in tool['publication']:
            if 'Primary' in publication['type']:
                doi = None

                if publication['doi'] != None:
                    doi = publication['doi']
                if publication['doi'] == None and publication['pmid'] != None:
                    doi = Doi.get_doi_from_pmid(publication['pmid'])
                    # print('*Get DOI from PMID: ' + str(doi))
                if publication['doi'] == None and publication['pmcid'] != None:
                    doi = Doi.get_doi_from_pmid(publication['pmcid'])

                if doi != None:
                    doi_entry, created = Doi.objects.get_or_create(doi=doi)
                    doi_entry.save()
                    self.primary_publication.add(doi_entry.id)

        # insert or get DB topic entry table here
        for topic in tool['topic']:
            if topic['uri'] == "http://edamontology.org/topic_3557":
                # cf comments in https://bioportal.bioontology.org/ontologies/EDAM?p=classes&conceptid=topic_3957
                # how could we do this not in the code ?
                topic['uri'] = "http://edamontology.org/topic_3957"
            topic_entry, created = Topic.objects.get_or_create(uri=topic['uri'])
            topic_entry.save()
            self.scientific_topics.add(topic_entry.id)

        # entry for toolCredit
        for credit in tool['credit']:
            toolCredit_entry, created = ToolCredit.objects.get_or_create(
                name=credit['name'],
                email=credit['email'],
                url=credit['url'],
                orcidid=credit['orcidid'],
                gridid=credit['gridid'],
                typeEntity=credit['typeEntity'],
                note=credit['note'],
            )
            toolCredit_entry.save()
            self.tool_credit.add(toolCredit_entry.id)

            # add typerole entry
            for type_role in credit['typeRole']:
                typeRole_entry, created = TypeRole.objects.get_or_create(name=type_role)
                typeRole_entry.save()
                toolCredit_entry.type_role.add(typeRole_entry.id)


@receiver(post_save, sender=Tool)
def update_information_from_biotool(sender, instance, created, **kwargs):
    if created and instance.biotoolsID is not None and instance.biotoolsID != "":
        instance.update_information_from_biotool()
