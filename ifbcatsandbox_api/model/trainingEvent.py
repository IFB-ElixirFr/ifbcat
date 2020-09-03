# Imports
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from ifbcatsandbox_api.model.computingFacility import ComputingFacility
from ifbcatsandbox_api.model.event import Event
from ifbcatsandbox_api.model.misc import AudienceType, AudienceRole, DifficultyLevelType
from ifbcatsandbox_api.model.trainingMaterial import TrainingMaterial
from ifbcatsandbox_api.model.userProfile import UserProfile


# Trainer model
class Trainer(models.Model):
    """Trainer model: A person who is providing training at a training event."""

    # trainerEmail is mandatory

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    trainerName = models.CharField(
        max_length=255, blank=True, help_text="Name of person who is providing training at the training event."
    )
    trainerEmail = models.EmailField(help_text="Email of person who is providing training at the training event.")

    trainerId = models.ForeignKey(
        UserProfile,
        related_name='trainerId',
        null=True,
        on_delete=models.SET_NULL,
        help_text="IFB ID of person who is providing training at the training event.",
    )

    def __str__(self):
        """Return the Trainer model as a string."""
        return self.trainerEmail.__str__()


# Training event model
class TrainingEvent(Event):
    """Training event model: An event dedicated to bioinformatics training or teaching."""

    # No fields are mandatory (beyond what's mandatory in Event)
    audienceTypes = models.ManyToManyField(
        AudienceType,
        blank=True,
        related_name='trainingEvents',
        help_text="The education or professional level of the expected audience of the training event.",
    )
    audienceRoles = models.ManyToManyField(
        AudienceRole,
        blank=True,
        related_name='trainingEvents',
        help_text="The professional roles of the expected audience of the training event.",
    )
    difficultyLevel = models.CharField(
        max_length=255,
        choices=DifficultyLevelType.choices,
        blank=True,
        help_text="The required experience and skills of the expected audience of the training event.",
    )
    trainingMaterials = models.ManyToManyField(
        TrainingMaterial,
        blank=True,
        related_name='trainingEvents',
        help_text="Training material that the training event uses.",
    )
    learningOutcomes = models.TextField(blank=True, help_text="Expected learning outcomes from the training event.")
    hoursPresentations = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Total time (hours) of presented training material.",
        validators=[MinValueValidator(1),],
    )
    hoursHandsOn = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Total time (hours) of hands-on / practical work.",
        validators=[MinValueValidator(1),],
    )
    hoursTotal = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Total time investment (hours) of the training event, including recommended prework.",
        validators=[MinValueValidator(1),],
    )
    trainers = models.ManyToManyField(
        Trainer,
        blank=True,
        related_name='trainingEvents',
        help_text="Details of people who are providing training at the training event.",
    )
    personalised = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the training is tailored to the individual in some way (BYOD, personal tutoring etc.)",
    )
    computingFacilities = models.ManyToManyField(
        ComputingFacility,
        blank=True,
        related_name='trainingEvents',
        help_text="Computing facilities that the training event uses.",
    )
    # databases
    # tools


# Training event metrics model
class TrainingEventMetrics(models.Model):
    """Training event metrics model: Metrics and other information for a specific training event."""

    # dateStart and dateEnd are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    dateStart = models.DateField(help_text="The start date of the training event.")
    dateEnd = models.DateField(help_text="The end date of the training event.")
    numParticipants = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of participants at the training event.",
        validators=[MinValueValidator(1),],
    )
    trainingEvent = models.ForeignKey(
        TrainingEvent,
        related_name='metrics',
        on_delete=models.CASCADE,
        help_text="Training event to which the metrics are associated.",
    )

    class Meta:
        verbose_name_plural = "Training event metrics"

    def __str__(self):
        """Return the TrainingEventMetrics model as a string."""
        return self.dateStart.__str__()
