import json
import logging

import requests
from Bio import Entrez
from django.core.exceptions import ValidationError
from django.db import models, DataError
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions, misc
from ifbcat_api.misc import BibliographicalEntryNotFound
from ifbcat_api.validators import validate_edam_topic, validate_can_be_looked_up, validate_doi
from ifbcat_api.validators import validate_grid_or_ror_id

logger = logging.getLogger(__name__)


class Licence(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Such as GLPv3, Apache 2.0, ...",
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.UserCanAddNew
            | permissions.UserCanEditAndDeleteIfNotUsed
            | permissions.ReadWriteByCurator
            | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )


class Topic(models.Model):
    """Event topic model: URI of EDAM Topic term describing scope or expertise."""

    # topic is mandatory
    uri = models.CharField(
        max_length=255,
        unique=True,
        help_text="URI of EDAM Topic term describing scope or expertise. "
        "Go to https://edamontology.github.io/edam-browser/#topic_0003 to find new topics.",
        validators=[
            validate_edam_topic,
        ],
    )

    label = models.CharField(
        max_length=255,
        blank=True,
    )

    description = models.TextField(
        max_length=255,
        blank=True,
        help_text="Definition of the EDAM term",
    )

    # https://docs.djangoproject.com/fr/3.1/ref/contrib/postgres/fields/
    synonyms = ArrayField(
        base_field=models.CharField(
            max_length=255,
        ),
        size=8,
        help_text="Narrow synonyms",
        blank=True,
        null=True,
    )

    @property
    def edam_id(self):
        return self.uri[24:]

    @property
    def edam_browser_url(self):
        return f'https://edamontology.github.io/edam-browser/#{self.edam_id}'

    def __str__(self):
        """Return the Topic model as a string."""
        return f'{self.label} ({self.uri})'

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.UserCanAddNew
            | permissions.UserCanEditAndDeleteIfNotUsed
            | permissions.SuperuserCanDelete,
            IsAuthenticatedOrReadOnly,
        )

    def update_information_from_ebi_ols(self):
        response = misc.get_edam_info_from_ols(self.uri)
        try:
            term = response["_embedded"]["terms"][0]
            if term["iri"] != self.uri:
                logger.error(f"Searched for {self.uri} but got a a response term {term['iri']} aborting update")
                return
            self.label = term["label"]
            self.description = term["description"][0] if isinstance(term["description"], list) else term["description"]
            self.synonyms = term["synonyms"]
            try:
                self.save()
            except DataError as e:
                logger.error(
                    f"Issue when saving topic {self.uri}, "
                    f"please investigate with https://www.ebi.ac.uk/ols/api/ontologies/edam/terms?iri={self.uri}"
                )
                raise
        except KeyError as e:
            logger.error(
                f"Issue when saving topic {self.uri}, please investigate "
                f"with https://www.ebi.ac.uk/ols/api/ontologies/edam/terms?iri={self.uri}\n{json.dumps(response)}"
            )
        # # code use to pre-load topics, and spare rest calls later, should remain commented on git
        # filepath = "./import_data/Topic.json"
        # try:
        #     with open(filepath) as f:
        #         topics = json.load(f)
        # except FileNotFoundError:
        #     topics = []
        # topics.append(
        #     dict(
        #         label=self.label,
        #         description=self.description,
        #         synonyms=self.synonyms,
        #         uri=self.uri,
        #     )
        # )
        # with open(filepath, 'w') as f:
        #     json.dump(topics, f)


@receiver(post_save, sender=Topic)
def update_information_from_ebi_ols(sender, instance, created, **kwargs):
    if created and (instance.label is None or instance.label == ""):
        instance.update_information_from_ebi_ols()


class Keyword(models.Model):
    """Keyword model: A keyword (beyond EDAM ontology scope)."""

    keyword = models.CharField(
        max_length=255,
        unique=True,
        help_text="A keyword (beyond EDAM ontology scope).",
        validators=[
            validate_can_be_looked_up,
        ],
    )

    def __str__(self):
        """Return the Keyword model as a string."""
        return self.keyword

    def clean_fields(self, exclude=None):
        super().clean_fields()
        if exclude is not None and "keyword" in exclude:
            return
        qs = Keyword.objects.filter(keyword__unaccent__iexact=self.keyword).filter(~Q(pk=self.pk))
        if qs.exists():
            raise ValidationError("Keyword \"%s\" already exists as \"%s\"" % (self.keyword, qs.get().keyword))

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.ReadWriteBySuperuser
            | permissions.ReadWriteByCurator
            | permissions.UserCanEditAndDeleteIfNotUsed,
            IsAuthenticatedOrReadOnly,
        )


class AudienceType(models.Model):
    """
    AudienceType model: The education or professional level of the expected audience of the training event or material.
    AudienceType has a many:many relationship to TrainingMaterial
    """

    # field is mandatory
    audienceType = models.CharField(
        max_length=255,
        # choices=AudienceTypeName.choices,  # AudienceTypeName moved to migration 0061
        unique=True,
        help_text="The education or professional level of the expected audience of the training event or material.",
    )

    def __str__(self):
        """Return the AudienceType model as a string."""
        return self.audienceType

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly | permissions.ReadWriteBySuperuser | permissions.ReadWriteByCurator,
            IsAuthenticatedOrReadOnly,
        )


class AudienceRole(models.Model):
    """
    AudienceRole model: The professional roles of the expected audience of the training event or material.
    AudienceRole has a many:many relationship to TrainingMaterial
    """

    # field is mandatory
    audienceRole = models.CharField(
        max_length=255,
        # choices=AudienceRoleName.choices,  # AudienceRoleName moved to migration 0061
        unique=True,
        help_text="The professional roles of the expected audience of the training event or material.",
    )

    def __str__(self):
        """Return the AudienceRole model as a string."""
        return self.audienceRole

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly | permissions.ReadWriteBySuperuser | permissions.ReadWriteByCurator,
            IsAuthenticatedOrReadOnly,
        )


class DifficultyLevelType(models.TextChoices):
    """Controlled vocabulary for training materials or events describing the required experience and skills of the expected audience."""

    NOVICE = 'Novice', _('Novice')
    INTERMEDIATE = 'Intermediate', _('Intermediate')
    ADVANCED = 'Advanced', _('Advanced')


class Field(models.Model):
    """Field model: A broad field that an organisation or bioinformatics team serves."""

    # field is mandatory
    field = models.CharField(
        max_length=255,
        # choices=OrganisationFieldName.choices, # OrganisationFieldName moved to migration 0058
        unique=True,
        help_text="A broad field that the organisation or bioinformatics serves.",
    )

    def __str__(self):
        """Return the Field model as a string."""
        return self.field

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly | permissions.ReadWriteBySuperuser | permissions.ReadWriteByCurator,
            IsAuthenticatedOrReadOnly,
        )


class Doi(models.Model):
    """Digital object identifier model: A digital object identifier (DOI) of a publication or training material."""

    doi = models.CharField(
        max_length=255,
        unique=True,
        help_text="A digital object identifier (DOI) of a publication or training material.",
        validators=[
            validate_doi,
        ],
    )
    title = models.TextField("Title", null=True, blank=True)
    journal_name = models.TextField("Journal name", null=True, blank=True)
    authors_list = models.TextField("Authors list", null=True, blank=True)
    biblio_year = models.PositiveSmallIntegerField("Year", null=True, blank=True)

    def __str__(self):
        """Return the Doi model as a string."""
        return f'{self.title} - {self.authors_list} ({self.doi})'

    def fill_from_doi(self):
        info = misc.get_doi_info(str(self.doi))
        self.title = info["title"]
        self.journal_name = info["journal_name"]
        self.authors_list = info["authors_list"]
        self.biblio_year = info["biblio_year"]

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.UserCanAddNew
            | permissions.UserCanDeleteIfNotUsed
            | permissions.SuperuserCanDelete
            | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )

    @classmethod
    def get_doi_from_pmid(cls, pmid):
        with Entrez.efetch(db="pubmed", id=str(pmid), rettype="xml", retmode="text") as handle:
            d = Entrez.read(handle)
            for article_id in d["PubmedArticle"][0]["PubmedData"]["ArticleIdList"]:
                if article_id[:2] == "10":
                    return article_id


@receiver(pre_save, sender=Doi)
def fetch_info_from_doi(sender, instance, **kwargs):
    if instance.pk is None and instance.doi is not None and instance.doi != "":
        try:
            instance.fill_from_doi()
        except BibliographicalEntryNotFound:
            pass
        except requests.HTTPError:
            logger.warning(f"Error while fetching {instance.doi}")


class WithGridIdOrRORId(models.Model):
    class Meta:
        abstract = True

    orgid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text="Organisation ID (GRID or ROR ID)",
        validators=[
            validate_grid_or_ror_id,
        ],
    )
