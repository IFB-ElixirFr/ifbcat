# Imports
from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.computingFacility import ComputingFacility
from ifbcat_api.model.event import AbstractEvent, Event
from ifbcat_api.model.misc import AudienceType, AudienceRole, DifficultyLevelType
from ifbcat_api.model.trainingMaterial import TrainingMaterial
from ifbcat_api.model.userProfile import UserProfile


class Trainer(models.Model):
    """Trainer model: A person who is providing training at a training event."""

    # trainerEmail is mandatory
    trainerName = models.CharField(
        max_length=255, blank=True, help_text="Name of person who is providing training at the training event."
    )
    trainerEmail = models.EmailField(help_text="Email of person who is providing training at the training event.")

    trainerId = models.ForeignKey(
        UserProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="IFB ID of person who is providing training at the training event.",
    )

    def __str__(self):
        """Return the Trainer model as a string."""
        return self.trainerEmail.__str__()

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.UserCanAddNew
            | permissions.UserCanEditAndDeleteIfNotUsed
            | permissions.ReadWriteBySuperuser,
            IsAuthenticatedOrReadOnly,
        )


class Training(AbstractEvent):
    """Training event model: An event dedicated to bioinformatics training or teaching."""

    # No fields are mandatory (beyond what's mandatory in Event)
    audienceTypes = models.ManyToManyField(
        AudienceType,
        blank=True,
        help_text="The education or professional level of the expected audience of the training event.",
    )
    audienceRoles = models.ManyToManyField(
        AudienceRole,
        blank=True,
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
        help_text="Training material that the training event uses.",
    )
    learningOutcomes = models.TextField(blank=True, help_text="Expected learning outcomes from the training event.")
    hoursPresentations = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Total time (hours) of presented training material.",
        validators=[
            MinValueValidator(1),
        ],
    )
    hoursHandsOn = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Total time (hours) of hands-on / practical work.",
        validators=[
            MinValueValidator(1),
        ],
    )
    hoursTotal = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Total time investment (hours) of the training event, including recommended prework.",
        validators=[
            MinValueValidator(1),
        ],
    )
    personalised = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the training is tailored to the individual in some way (BYOD, personal tutoring etc.)",
    )
    computingFacilities = models.ManyToManyField(
        ComputingFacility,
        blank=True,
        help_text="Computing facilities that the training event uses.",
    )
    prerequisites_trainings = models.ManyToManyField(
        to="Training",
        blank=True,
        help_text="Trainings (ideally) already followed by the audience, or at least possess the expected outcomes.",
    )
    tess_publishing = models.BooleanField(
        default=True,
        help_text="Publish it in tess? Does associated events should also be published (unless explicitly indicated)?",
    )

    @classmethod
    def get_edition_permission_classes(cls):
        return super().get_edition_permission_classes() + (
            permissions.ReadWriteByContact,
            permissions.ReadWriteBySuperEditor,
        )

    # @classmethod
    # def get_default_permission_classes(cls):
    #     return (IsAuthenticated,)

    def create_new_event(self, start_date, end_date):
        event_attrs = dict(
            name=f'New session of {self.name}',
            type=Event.EventType.TRAINING_COURSE,
            training=self,
        )
        if self.shortName:
            event_attrs['shortName'] = f'New session of {self.shortName}'
        for field in [
            'description',
            'homepage',
            'onlineOnly',
            'accessibility',
            'accessibilityNote',
            'maxParticipants',
            'contactName',
            'contactEmail',
            'contactId',
            'logo_url',
        ]:
            event_attrs[field] = getattr(self, field)
        event = Event.objects.create(**event_attrs)

        if start_date:
            event_attrs['start_date'] = start_date
            event_attrs['end_date'] = end_date

        for m2m_name in [
            'costs',
            'topics',
            'keywords',
            'prerequisites',
            'elixirPlatforms',
            'communities',
            'organisedByTeams',
            'organisedByOrganisations',
            'sponsoredBy',
        ]:
            for o in getattr(self, m2m_name).all():
                getattr(event, m2m_name).add(o)

        return event
