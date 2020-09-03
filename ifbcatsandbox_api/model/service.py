from django.conf import settings
from django.db import models

from ifbcatsandbox_api.model.bioinformaticsTeam import BioinformaticsTeam
from ifbcatsandbox_api.model.misc import Doi
from ifbcatsandbox_api.model.trainingEvent import TrainingEvent
from ifbcatsandbox_api.model.trainingMaterial import TrainingMaterial
from ifbcatsandbox_api.validators import validate_can_be_looked_up


class Service(models.Model):
    """Service model: A provision of a bundle of computing facilities, databases, tools, training events and materials, with support to help end-users utilise the resources."""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    # name, description, dateEstablished & bioinformaticsTeam are mandatory
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
    bioinformaticsTeams = models.ManyToManyField(
        BioinformaticsTeam,
        related_name='services',
        help_text="The bioinformatics team(s) that provides this service.",
    )
    computingFacilities = models.ManyToManyField(
        BioinformaticsTeam,
        blank=True,
        related_name='servicesComputingFacilities',
        help_text="Computing facilities provided by the service.",
    )
    trainingEvents = models.ManyToManyField(
        TrainingEvent,
        blank=True,
        related_name='services',
        help_text="Training event(s) provided by the service.",
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
