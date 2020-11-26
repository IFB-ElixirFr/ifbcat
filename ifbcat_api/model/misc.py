import json
import logging

from Bio import Entrez
from django.core.exceptions import ValidationError
from django.db import models, DataError
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField
from pip._vendor import requests
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.validators import validate_edam_topic, validate_can_be_looked_up, validate_doi

logger = logging.getLogger(__name__)


class Topic(models.Model):
    """Event topic model: URI of EDAM Topic term describing scope or expertise."""

    # topic is mandatory
    uri = models.CharField(
        max_length=255,
        unique=True,
        help_text="URI of EDAM Topic term describing scope or expertise.",
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

    def __str__(self):
        """Return the Topic model as a string."""
        return self.uri

    @classmethod
    def get_permission_classes(cls):
        return (permissions.PubliclyReadableByUsersEditableBySuperuser, IsAuthenticatedOrReadOnly)

    def update_information_from_ebi_ols(self):
        url = f'https://www.ebi.ac.uk/ols/api/ontologies/edam/terms?iri={self.uri}'
        response = requests.get(url).json()
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
            logger.error(f"Issue when saving topic {self.uri}, please investigate with {url}")
            raise
        # code use to pre-load topics, and spare rest calls later
        filepath = "./import_data/topics.json"
        try:
            with open(filepath) as f:
                topics = json.load(f)
        except FileNotFoundError:
            topics = []
        topics.append(
            dict(
                label=self.label,
                description=self.description,
                synonyms=self.synonyms,
                uri=self.uri,
            )
        )
        with open(filepath, 'w') as f:
            json.dump(topics, f)


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
        return (permissions.PubliclyReadableByUsers, IsAuthenticatedOrReadOnly)


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
        return (permissions.PubliclyReadableByUsersEditableBySuperuser,)


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
        return (permissions.PubliclyReadableByUsersEditableBySuperuser,)


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

    def __str__(self):
        """Return the Doi model as a string."""
        return self.doi

    @classmethod
    def get_permission_classes(cls):
        return (permissions.PubliclyReadableByUsersEditableBySuperuser,)

    @classmethod
    def get_doi_from_pmid(cls, pmid):
        with Entrez.efetch(db="pubmed", id=str(pmid), rettype="xml", retmode="text") as handle:
            d = Entrez.read(handle)
            for article_id in d["PubmedArticle"][0]["PubmedData"]["ArticleIdList"]:
                if article_id[:2] == "10":
                    return article_id
