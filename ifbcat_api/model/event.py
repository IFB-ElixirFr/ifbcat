# Imports
import functools

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, ManyToManyRel, ManyToOneRel, Case, When, Value, BooleanField, Q

from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.community import Community
from ifbcat_api.model.computingFacility import ComputingFacility
from ifbcat_api.model.elixirPlatform import ElixirPlatform
from ifbcat_api.model.misc import Topic, Keyword
from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team
from ifbcat_api.model.trainingMaterial import TrainingMaterial
from ifbcat_api.model.userProfile import UserProfile


# Event prerequisite model
class EventPrerequisite(models.Model):
    """Event prerequisite model: A skill which the audience should (ideally) possess to get the most out of the event, e.g. "Python"."""

    # prerequisite is mandatory
    prerequisite = models.CharField(
        max_length=255,
        unique=True,
        help_text="A skill which the audience should (ideally) possess to get the most out of the event, e.g. 'Python'.",
    )

    def __str__(self):
        """Return the EventPrerequisite model as a string."""
        return self.prerequisite

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


# Event cost model
class EventCost(models.Model):
    """Event cost model: Monetary cost to attend the event, e.g. 'Free to academics'."""

    # cost is mandatory
    cost = models.CharField(
        max_length=255,
        # choices=CostType.choices, # CostType moved to migration 0057
        unique=True,
        help_text="Monetary cost to attend the event, e.g. 'Free to academics'.",
    )

    def __str__(self):
        """Return the EventCost model as a string."""
        return self.cost

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


# Event sponsor model
class EventSponsor(models.Model):
    """Event sponsor model: A sponsor of an event."""

    # name & homepage are mandatory
    name = models.CharField(
        max_length=255, unique=True, help_text="Name of institutional entity that is sponsoring the event."
    )
    homepage = models.URLField(max_length=255, help_text="Homepage URL of the sponsor of the event.")
    logo_url = models.URLField(max_length=512, help_text="URL of logo of event sponsor.", blank=True, null=True)
    organisationId = models.ForeignKey(
        Organisation,
        null=True,
        on_delete=models.SET_NULL,
        help_text="IFB ID of a event-sponsoring organisation registered in the IFB catalogue.",
    )

    def __str__(self):
        """Return the EventSponsor model as a string."""
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


class AbstractEvent(models.Model):
    class Meta:
        abstract = True

    """Event model: A scheduled scholarly gathering such as workshop, conference, symposium, training or open project meeting of relevance to bioinformatics."""

    # Controlled vocabularies
    # See https://docs.django(project).com/en/dev/ref/models/fields/#enumeration-types
    # The enums support internatonalization (using the '_' shorthand convention for gettext_lazy() function)
    # See https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#internationalization-in-python-code

    # EventOpenToType: Controlled vocabulary for whether an event is everyone, internal personnel or others.
    class EventOpenToType(models.TextChoices):
        """Controlled vocabulary for whether an event is opened to Everyone, Internal personnel or Others."""

        EVERYONE = 'Everyone', _('Everyone')
        INTERNAL_PERSONNEL = 'Internal personnel', _('Internal personnel')
        OTHERS = 'Others', _('Others')

    # name, description, homepage, openTo, contactName and contactEmail are mandatory
    name = models.CharField(
        max_length=255,
        help_text="Full name / title of the event.",
    )
    shortName = models.CharField(max_length=255, blank=True, help_text="Short name (or acronym) of the event.")
    description = models.TextField(help_text="Description of the event.")
    homepage = models.URLField(
        max_length=255,
        blank=True,
        help_text="URL of event homepage.",
    )
    costs = models.ManyToManyField(
        EventCost,
        blank=True,
        help_text="Monetary cost to attend the event, e.g. 'Free to academics'.",
    )
    topics = models.ManyToManyField(
        Topic,
        blank=True,
        help_text="URIs of EDAM Topic terms describing the scope of the event.",
    )
    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        help_text="A keyword (beyond EDAM ontology scope) describing the event.",
    )
    prerequisites = models.ManyToManyField(
        EventPrerequisite,
        blank=True,
        help_text="A skill which the audience should (ideally) possess to get the most out of the event, e.g. 'Python'.",
    )
    openTo = models.CharField(
        max_length=255,
        choices=EventOpenToType.choices,
        help_text="Whether the event is for everyone, internal personnel or others.",
    )
    accessConditions = models.TextField(
        help_text="Comment on how one can access. Mandatory if not open to everyone",
        blank=True,
        null=True,
    )
    maxParticipants = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants to the event.",
        validators=[
            MinValueValidator(1),
        ],
    )
    contactName = models.CharField(max_length=255, help_text="Name of person to contact about the event.")
    contactEmail = models.EmailField(help_text="Email of person to contact about the event.")
    contactId = models.ForeignKey(
        UserProfile,
        null=True,
        on_delete=models.SET_NULL,
        help_text="IFB ID of person to contact about the event.",
    )
    elixirPlatforms = models.ManyToManyField(
        ElixirPlatform,
        blank=True,
        help_text="ELIXIR Platform to which it is relevant.",
    )
    communities = models.ManyToManyField(
        Community,
        blank=True,
        help_text="Community for which it is relevant.",
    )
    # hostedBy = models.ManyToManyField(
    #     Organisation, blank=True, help_text="Organisation which is hosting the event."
    # )
    organisedByTeams = models.ManyToManyField(
        Team,
        blank=True,
        help_text="A Team that is organizing it.",
    )
    organisedByOrganisations = models.ManyToManyField(
        Organisation,
        blank=True,
        help_text="An organisation that is organizing it.",
    )
    sponsoredBy = models.ManyToManyField(
        EventSponsor,
        blank=True,
        help_text="An institutional entity that is sponsoring it.",
    )
    logo_url = models.URLField(max_length=512, help_text="URL of logo of event.", blank=True, null=True)
    is_draft = models.BooleanField(
        default=False,
        help_text="Mention whether it's a draft.",
    )
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

    def clean(self):
        if self.openTo != self.EventOpenToType.EVERYONE and len(self.accessConditions or '') == 0:
            raise ValidationError(dict(accessConditions="Details have to be provided when openTo is not Everyone"))

    def __str__(self):
        """Return the Event model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            functools.reduce(lambda a, b: a | b, cls.get_edition_permission_classes()),
            functools.reduce(lambda a, b: a | b, cls.get_default_permission_classes()),
        )

    @classmethod
    def get_default_permission_classes(cls):
        return (IsAuthenticatedOrReadOnly,)

    @classmethod
    def get_edition_permission_classes(cls):
        return (
            permissions.ReadOnly,
            permissions.UserCanAddNew,
            permissions.ReadWriteByContact,
            permissions.ReadWriteByOrgByTeamsLeader,
            permissions.ReadWriteByOrgByTeamsDeputies,
            permissions.ReadWriteByOrgByTeamsMaintainers,
            # permissions.ReadWriteByOrgByOrganisationsLeader,
            permissions.ReadWriteBySuperEditor,
            permissions.ReadWriteByCurator,
        )


class Event(AbstractEvent):
    # EventType: Controlled vocabulary of types of events.
    # Name and human-readable labels are set the same (rather than using an short-form abbreviation for the name), because of issue:
    # see https://github.com/joncison/ifbcat-sandbox/pull/9
    class EventType(models.TextChoices):
        """Controlled vocabulary of types of events."""

        WORKSHOP = 'Workshop', _('Workshop')
        TRAINING_COURSE = 'Training course', _('Training session')
        MEETING = 'Meeting', _('Meeting')
        CONFERENCE = 'Conference', _('Conference')

    class CourseModeType(models.TextChoices):
        ONLINE = 'Online', _('Online')
        ONSITE = 'Onsite', _('Onsite')
        BLENDED = 'Blended', _('Blended')

    courseMode = models.CharField(
        choices=CourseModeType.choices,
        default=None,
        max_length=10,
        null=True,
        blank=False,  # Do not allow to set a blank value in the UI, only allow programmatically
        help_text="Select the mode for this event",
    )
    registration_opening = models.DateField(
        help_text="When does the registration for the event opens.",
        blank=True,
        null=True,
    )
    registration_closing = models.DateField(
        help_text="When does the registration for the event closes.",
        blank=True,
        null=True,
    )
    start_date = models.DateField(
        help_text="Set the start date of the event",
        blank="True",
        null=True,
    )
    end_date = models.DateField(
        help_text="Set the end date of the event",
        blank=True,
        null=True,
    )
    type = models.CharField(
        max_length=255,
        blank=True,
        choices=EventType.choices,
        help_text="The type of event e.g. 'Training session'.",
    )
    venue = models.TextField(
        blank=True,
        help_text="The address of the venue where the event will be held.",
    )
    city = models.CharField(
        max_length=255,
        blank=True,
        help_text="The nearest city to where the event will be held.",
    )
    country = models.CharField(
        max_length=255,
        blank=True,
        help_text="The country where the event will be held.",
    )
    geographical_range = models.CharField(
        max_length=255,
        blank=True,
        help_text="Geographical area which is the focus of event marketing efforts.",
        choices=[
            ('Local', 'Local or regional'),
            ('National', 'National'),
            ('International', 'International'),
        ],
    )
    training = models.ForeignKey(
        to="Training",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="The training proposed, must be provided if event type is 'Training session'.",
    )
    trainers = models.ManyToManyField(
        to="Trainer",
        blank=True,
        help_text="Details of people who are providing training at the event.",
    )
    trainingMaterials = models.ManyToManyField(
        TrainingMaterial,
        blank=True,
        help_text="Training material related to the training session.",
    )
    computingFacilities = models.ManyToManyField(
        ComputingFacility,
        blank=True,
        help_text="Computing facilities that are used in the event.",
    )
    tess_publishing = models.IntegerField(
        default=2,
        choices=((0, "No"), (1, "Yes"), (2, "Auto")),
        help_text="Publish it in tess? Auto use training status for training sessions, or Yes otherwise for",
    )

    @classmethod
    def annotate_is_tess_publishing(cls, qs=None):
        if qs is None:
            qs = cls.objects
        return qs.annotate(
            is_tess_publishing=Case(
                When(tess_publishing=1, then=True),
                When(
                    Q(tess_publishing=2)
                    & (~Q(type=Event.EventType.TRAINING_COURSE) | Q(training__tess_publishing=True)),
                    then=True,
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
        )

    def clean(self):
        super().clean()
        errors = {}
        if self.type == Event.EventType.TRAINING_COURSE and self.training is None:
            errors.setdefault('training', []).append("training must be provided when creating a Training session")
        if not self.is_draft and self.start_date is None:
            errors.setdefault('start_date', []).append("start date must be provided if the event is not a draft")
        if self.end_date and self.start_date is None:
            errors.setdefault('start_date', []).append("start date must be provided if end date is")
        if len(errors) > 0:
            raise ValidationError(errors)

    @classmethod
    def get_edition_permission_classes(cls):
        return super().get_edition_permission_classes() + (permissions.ReadWriteByTrainers,)
