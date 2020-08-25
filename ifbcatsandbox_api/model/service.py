from django.db import models

from ifbcatsandbox_api.model.userProfile import *

# Resource model
class Service(models.Model):
    """Service model: A provision of a bundle of computing facilities, databases, tools, training events and materials, with support to help end-users utilise the resources."""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    # name, description, dateEstablished & bioinformaticsTeam are mandatory
    name = models.CharField(max_length=255, help_text="Name of the service.")
    description = models.TextField(help_text="Short desccripion of the service.")
    dateEstablished = models.DateField(help_text="Date when the service was first established and started operating.")
    bioinformaticsTeams = models.ManyToManyField(
        BioinformaticsTeam, related_name='services', help_text="The bioinformatics team(s) that provides this service.",
    )
    computingFacilities = models.ManyToManyField(
        BioinformaticsTeam,
        blank=True,
        related_name='services',
        help_text="Computing facilities provided by the service.",
    )
    trainingEvents = models.ManyToManyField(
        TrainingEvent, blank=True, related_name='services', help_text="Training event(s) provided by the service.",
    )
    TrainingMaterials = models.ManyToManyField(
        TrainingMaterial,
        blank=True,
        related_name='services',
        help_text="Training material(s) provided by the service.",
    )
    publications = models.ManyToManyField(
        Doi, related_name='services', blank=True, help_text="Publication(s) that describe the service as a whole.",
    )
    governanceSab = models.URLField(
        max_length=255, null=True, blank=True, help_text="Link to the description of the SAB covering the service."
    )

    def __str__(self):
        """Return the Service model as a string."""
        return self.name
