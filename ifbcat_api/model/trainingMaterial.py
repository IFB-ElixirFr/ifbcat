# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.misc import Keyword, Topic, AudienceRole, AudienceType, DifficultyLevelType, Doi, Licence
from ifbcat_api.model.resource import Resource
from ifbcat_api.model.team import Team


class TrainingMaterial(Resource):
    """Training material model: Digital media such as a presentation or tutorial that can be used for bioinformatics training or teaching."""

    # fileLocation, fileName is mandatory
    # TO-DO:  providedBy
    # DOI is not mandatory, but if specified must be unique, so we cannot have blank=True.
    # Two NULL values do not equate to being the same, whereas two blank values would!
    doi = models.ForeignKey(
        Doi,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Unique identier (DOI) of the training material, e.g. a Zenodo DOI.",
    )
    fileLocation = models.URLField(
        max_length=255, help_text="A link to where the training material can be downloaded or accessed."
    )
    fileName = models.CharField(
        max_length=255, help_text="The name of a downloadable file containing the training material."
    )
    topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='trainingMaterials',
        help_text="URIs of EDAM Topic terms describing the scope of the training material.",
    )
    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        related_name='trainingMaterials',
        help_text="A keyword (beyond EDAM ontology scope) describing the training material.",
    )
    audienceTypes = models.ManyToManyField(
        AudienceType,
        blank=True,
        related_name='trainingMaterials',
        help_text="The education or professional level of the expected audience of the training material.",
    )
    audienceRoles = models.ManyToManyField(
        AudienceRole,
        blank=True,
        related_name='trainingMaterials',
        help_text="The professional roles of the expected audience of the training material.",
    )
    difficultyLevel = models.CharField(
        max_length=255,
        choices=DifficultyLevelType.choices,
        blank=True,
        help_text="The required experience and skills of the expected audience of the training material.",
    )
    providedBy = models.ManyToManyField(
        Team,
        blank=True,
        related_name='trainingMaterials',
        help_text="The team that provides the training material.",
    )
    dateCreation = models.DateField(blank=True, null=True, help_text="Date when the training material was created.")
    dateUpdate = models.DateField(blank=True, null=True, help_text="Date when the training material was updated.")
    licence = models.ManyToManyField(
        Licence,
        blank=True,
        help_text="Licence under which the training material is made available.",
    )

    def __str__(self):
        """Return the TrainingMaterial model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.ReadWriteByProvidedByLeader
            | permissions.ReadWriteByProvidedByDeputies
            | permissions.ReadWriteByProvidedByMaintainer
            | permissions.ReadWriteByCurator
            | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )
