from django.db import models
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.misc import Doi
from ifbcat_api.model.team import Team

from ifbcat_api.model.training import Training
from ifbcat_api.model.trainingMaterial import TrainingMaterial
from ifbcat_api.validators import validate_can_be_looked_up


class Service(models.Model):
    """Service model: A provision of a bundle of computing facilities, databases, tools, training events and materials, with support to help end-users utilise the resources."""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the service.",
        validators=[
            validate_can_be_looked_up,
        ],
    )
    description = models.TextField(help_text="Short description of the service.")
    dateEstablished = models.DateField(help_text="Date when the service was first established and started operating.")
    teams = models.ManyToManyField(
        Team,
        related_name='services',
        help_text="The bioinformatics team(s) that provides this service.",
    )
    computingFacilities = models.ManyToManyField(
        Team,
        blank=True,
        related_name='servicesComputingFacilities',
        help_text="Computing facilities provided by the service.",
    )
    trainings = models.ManyToManyField(
        Training,
        blank=True,
        related_name='services',
        help_text="Training provided by the service.",
    )
    trainingMaterials = models.ManyToManyField(
        TrainingMaterial,
        blank=True,
        related_name='servicesTrainingMaterials',
        help_text="Training material(s) provided by the service.",
    )
    publications = models.ManyToManyField(
        Doi,
        related_name='services',
        blank=True,
        help_text="Publication(s) that describe the service as a whole.",
    )
    governanceSab = models.URLField(
        max_length=255, blank=True, null=True, help_text="Link to the description of the SAB covering the service."
    )

    def __str__(self):
        """Return the Service model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.ReadWriteByTeamsLeader
            | permissions.ReadWriteByTeamsDeputies
            | permissions.ReadWriteByTeamsMaintainers
            | permissions.ReadWriteByCurator
            | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )
