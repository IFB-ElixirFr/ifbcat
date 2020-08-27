# Imports
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from ifbcatsandbox_api.model.organisation import *
from ifbcatsandbox_api.model.elixirPlatform import *
from ifbcatsandbox_api.model.community import *
from ifbcatsandbox_api.model.misc import *


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


# Event sponsor model
class EventSponsor(models.Model):
    """Event sponsor model: A sponsor of an event."""

    # name & homepage are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, help_text="Name of institutional entity that is sponsoring the event.")
    homepage = models.URLField(max_length=255, help_text="Homepage URL of the sponsor of the event.")
    # TO-DO logo
    organisationId = models.ForeignKey(
        Organisation,
        related_name='eventSponsor',
        null=True,
        on_delete=models.SET_NULL,
        help_text="IFB ID of a event-sponsoring organisation registered in the IFB catalogue.",
    )

    def __str__(self):
        """Return the EventSponsor model as a string."""
        return self.name


# Event model
class Event(models.Model):
    """Event model: A scheduled scholarly gathering such as workshop, conference, symposium, training or open project meeting of relevance to bioinformatics."""

    # "on_delete=models.NULL" means that the Event is not deleted if the user profile is deleted.
    # "null=True" is required in case a user profile IS deleted.
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # Controlled vocabularies
    # See https://docs.django(project).com/en/dev/ref/models/fields/#enumeration-types
    # The enums support internatonalization (using the '_' shorthand convention for gettext_lazy() function)
    # See https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#internationalization-in-python-code

    # EventType: Controlled vocabulary of types of events.
    # Name and human-readable labels are set the same (rather than using an short-form abbreviation for the name), because of issue:
    # see https://github.com/joncison/ifbcat-sandbox/pull/9
    class EventType(models.TextChoices):
        """Controlled vocabulary of types of events."""

        WORKSHOP = 'Workshop', _('Workshop')
        TRAINING_COURSE = 'Training course', _('Training course')
        MEETING = 'Meeting', _('Meeting')
        CONFERENCE = 'Conference', _('Conference')

    # EventAccessibilityType: Controlled vocabulary for whether an event is public or private.
    class EventAccessibilityType(models.TextChoices):
        """Controlled vocabulary for whether an event is public or private."""

        PUBLIC = 'Public', _('Public')
        PRIVATE = 'Private', _('Private')

    # name, description, homepage, accessibility, contactName and contactEmail are mandatory
    name = models.CharField(
        max_length=255,
        help_text="Full name / title of the event.",
        validators=[
            validators.RegexValidator(r'^[a-zA-Z0-9 \-_~]+$', 'Should only contains char such as ^[a-zA-Z0-9\-_~]'),
        ],
    )
    shortName = models.CharField(max_length=255, blank=True, help_text="Short name (or acronym) of the event.")
    description = models.TextField(help_text="Description of the event.")
    homepage = models.URLField(max_length=255, null=True, blank=True, help_text="URL of event homepage.")

    # NB: max_length is mandatory, but is ignored by sqlite3, see https://github.com/joncison/ifbcat-sandbox/pull/9
    type = models.CharField(
        max_length=255, choices=EventType.choices, blank=True, help_text="The type of event e.g. 'Training course'."
    )

    dates = models.ManyToManyField(
        "EventDate",
        related_name='events',
        help_text="Date(s) and optional time periods on which the event takes place.",
    )
    venue = models.TextField(blank=True, help_text="The address of the venue where the event will be held.")
    city = models.CharField(max_length=255, blank=True, help_text="The nearest city to where the event will be held.")
    country = models.CharField(max_length=255, blank=True, help_text="The country where the event will be held.")
    onlineOnly = models.BooleanField(null=True, blank=True, help_text="Whether the event is hosted online only.")
    costs = models.ManyToManyField(
        EventCost, related_name='events', help_text="Monetary cost to attend the event, e.g. 'Free to academics'."
    )
    topics = models.ManyToManyField(
        Topic, related_name='events', help_text="URIs of EDAM Topic terms describing the scope of the event."
    )
    keywords = models.ManyToManyField(
        Keyword, related_name='events', help_text="A keyword (beyond EDAM ontology scope) describing the event."
    )
    prerequisites = models.ManyToManyField(
        EventPrerequisite,
        related_name='events',
        help_text="A skill which the audience should (ideally) possess to get the most out of the event, e.g. 'Python'.",
    )
    accessibility = models.CharField(
        max_length=255,
        choices=EventAccessibilityType.choices,
        blank=True,
        help_text="Whether the event is public or private.",
    )
    accessibilityNote = models.CharField(
        max_length=255, blank=True, help_text="Comment about the audience a private event is open to and tailored for."
    )
    maxParticipants = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants to the event.",
        validators=[MinValueValidator(1),],
    )
    contactName = models.CharField(max_length=255, help_text="Name of person to contact about the event.")
    contactEmail = models.EmailField(help_text="Email of person to contact about the event.")
    contactId = models.ForeignKey(
        UserProfile,
        related_name='eventContactId',
        null=True,
        on_delete=models.SET_NULL,
        help_text="IFB ID of person to contact about the event.",
    )
    market = models.CharField(
        max_length=255, blank=True, help_text="Geographical area which is the focus of event marketing efforts."
    )
    elixirPlatforms = models.ManyToManyField(
        ElixirPlatform, blank=True, related_name='events', help_text="ELIXIR Platform to which the event is relevant."
    )
    communities = models.ManyToManyField(
        Community, blank=True, related_name='events', help_text="Community for which the event is relevant."
    )
    hostedBy = models.ManyToManyField(
        Organisation, blank=True, related_name='events', help_text="Organisation which is hosting the event."
    )

    # organisedBy = ... TO_DO
    sponsoredBy = models.ManyToManyField(
        EventSponsor,
        blank=True,
        related_name='events',
        help_text="An institutional entity that is sponsoring the event.",
    )
    # logo = ... TO_DO

    def __str__(self):
        """Return the Event model as a string."""
        return self.name


# Event date model
# Event date has a many:one relationship to Event
class EventDate(models.Model):
    """Event date model: Start and end date and time of an event."""

    # dateStart is mandatory (other fields optional)
    dateStart = models.DateField(help_text="The start date of the event.")
    dateEnd = models.DateField(blank=True, null=True, help_text="The end date of the event.")
    timeStart = models.TimeField(blank=True, null=True, help_text="The start time of the event.")
    timeEnd = models.TimeField(blank=True, null=True, help_text="The end time of the event.")

    def __str__(self):
        """Return the EventDate model as a string."""
        return self.dateStart.__str__()
