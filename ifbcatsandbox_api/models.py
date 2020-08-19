# Imports
# AbstractBaseUser and PermissionsMixin are the base classes used when customising the Django user model
# BaseUserManager is the default user manager that comes with Django
# see https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#auth-custom-user
# "settings" is for retrieving settings from settings.py file (project file)
#
# "gettext_lazy" is used to mark text (specically terms from controlled vocabularies) to support internatonalization.
# "gettext_lazy as _" defines '_()' as an alias for '_gettext_lazy()' - it's just a shorthand convention.
# see https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#internationalization-in-python-code
# This "lazy" version of gettext() holds a reference to the translation string instead of the actual translated text,
# so the translation occurs when the value is accessed rather than when they’re called.  We need this behaviour so
# users will see the right language in their UI - see https://simpleisbetterthancomplex.com/tips/2016/10/17/django-tip-18-translations.html
# See https://simpleisbetterthancomplex.com/tips/2016/10/17/django-tip-18-translations.html
from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.conf import settings

# from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


# Manager for custom user profile model
# For more on user models with authentication see https://github.com/django/django/blob/stable/3.0.x/django/contrib/auth/models.py#L131-L158
class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    # Function that Django CLI will use when creating users
    # password=None means that if a password is not set it wil default to None,
    # preventing authentication with the user until a password is set.
    def create_user(self, firstname, lastname, email, orcidid=None, homepage=None, password=None):
        """Create a new user profile"""
        if not firstname:
            raise ValueError('Users must have a first (given) name.')
        if not lastname:
            raise ValueError('Users must have a last (family) name.')
        if not email:
            raise ValueError('Users must have an email address.')

        # Normalize the email address (makes the 2nd part of the address all lowercase)
        email = self.normalize_email(email)
        user = self.model(firstname=firstname, lastname=lastname, email=email, orcidid=orcidid, homepage=homepage)

        # Set password will encrypt the provided password - good practice to do so!
        # Even thoough there's only one database, it's good practice to name the databaes anyway, using:
        # user.save(using=self._db)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # Function for creating super-users
    # NB. all superusers must have a password, hence no "password=Nane"
    def create_superuser(self, firstname, lastname, email, password, orcidid=None, homepage=None):
        """Create a new superuser profile"""

        user = self.create_user(
            password=password, firstname=firstname, lastname=lastname, email=email, orcidid=orcidid, homepage=homepage,
        )

        # .is_superuser and is_staff come from PermissionsMixin
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


# Custom user profile model
#
# User profiles are set by default to be active (is_active = ...) and are not staff (is_staff = ...)
# NB. staff users have access to Django admin etc.
# NB. The model is registered with Django admin in admin.py.  Django will use the class name (UserProfile)
# to create a name ("User Profiles") for the model used in the admin interface, e.g. http://127.0.0.1:8000/admin/
# Thus it's best practice to name the class "UserProfile" and not "UserProfiles"
# NB. For a list of attributes of the fields see https://docs.djangoproject.com/en/3.0/ref/models/fields/
#
# "blank=true" allows empty fields in data entry forms
# "null=true" means emptry values will be stored as NULL in the database
# NB. Both "blank=True" and "unique=True" are set for orcidid to avoid unique constraint violations when saving multiple objects with blank values.
# null is used because two null values ARE considered unique when compared (in contrast to two blank values, which are considered non-unique)
# Normally only "blank=True" is set for string-based fields (CharField, TextField)... see https://docs.djangoproject.com/en/3.0/ref/models/fields/#null


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """UserProfile model: a user in the system."""

    # firstname, lastname and email are mandatory
    firstname = models.CharField(max_length=255, help_text="First (or given) name of a person (IFB catalogue user).")
    lastname = models.CharField(max_length=255, help_text="Last (or family) name of a person (IFB catalogue user).")
    orcidid = models.CharField(
        max_length=255, null=True, blank=True, unique=True, help_text="ORCID ID of a person (IFB catalogue user)."
    )
    email = models.EmailField(max_length=255, unique=True, help_text="Email address of a person (IFB catalogue user).")
    homepage = models.URLField(
        max_length=255, null=True, blank=True, help_text="Homepage of a person (IFB catalogue user)."
    )
    # expertise = ... TO_DO

    is_active = models.BooleanField(default=True, help_text="Whether a user account is active.")
    is_staff = models.BooleanField(default=False, help_text="Whether a user has staff status.")

    # Model manager to setup our custom user model for use with Django CLI (for user creation etc.)
    objects = UserProfileManager()

    # Override default username field with email address, and set other require fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    # Functions allowing Django to interact with our custom user model
    def get_full_name(self):
        """Retrieve full name of user"""
        fullname = self.firstname + ' ' + self.lastname
        return fullname

    def get_short_name(self):
        """Retrieve short name of user"""
        return self.firstname

    # Good practice to support string representation of the custom user model.
    def __str__(self):
        """Return string representation of our user."""
        return self.email


# News item model
# Users can create News items; a NewsItem object is associated with the user who created it.
class NewsItem(models.Model):
    """NewsItem model: a news item created by a user."""

    # Foreign key is used to associate this model to the UserProfile model.
    # This sets up a foreign key relationship in the backend database, ensuring integrity
    # (so a news item cannot be created for user profile that doesn't exist)
    #
    # NB. "settings.AUTH_USER_MODEL" is used to retrieve the auth user model from settings.py
    # Could instead have hardcoded UserProfile but that wouldn't be good practice
    #  (e.g. in case in future we wanted to revert back to using the default Django model)
    #
    # NB. "on_delete=models.CASCADE," means that if the user profile is removed,
    # then the associated news items are also deleted.
    # Could set the field to SET_NULL instead (if we wanted to preserve the news items) - then "null=True" must also be set
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # news and created_on are mandatory
    # "auto_now_add=True" means that the date/time stamp gets added automatically when the item is created.
    news = models.CharField(max_length=255, help_text="Some news provided by a user.")
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the NewsItem model as a string."""
        return self.news


# Event keyword model
# Keywords have a many:one relationship to Event
class EventKeyword(models.Model):
    """Event keyword model: A keyword (beyond EDAM ontology scope) describing the event."""

    keyword = models.CharField(
        max_length=255, unique=True, help_text="A keyword (beyond EDAM ontology scope) describing the event."
    )

    def __str__(self):
        """Return the EventKeyword model as a string."""
        return self.keyword


# Event prerequisite model
# Prerequisites have a many:one relationship to Event
# Same code as for EventKeyword
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


# Event topic model
# Event topic has a many:many relationship to Event
class EventTopic(models.Model):
    """Event topic model: URI of EDAM Topic term describing the scope of the event."""

    # topic is mandatory
    topic = models.CharField(
        max_length=255, unique=True, help_text="URI of EDAM Topic term describing the scope of the event."
    )

    def __str__(self):
        """Return the EventTopic model as a string."""
        return self.topic


# Event cost model
# Event cost has a many:many relationship to Event
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


# ELIXIR Platform model
class ElixirPlatform(models.Model):
    """ELIXIR Platform model: An official ELIXIR Platform, bringing together experts to define the strategy and provide services in a particular area."""

    # EventType: Controlled vocabulary of types of events.
    class ElixirPlatformName(models.TextChoices):
        """Controlled vocabulary of names of ELIXIR Platforms."""

        DATA = 'Data', _('Data')
        TOOLS = 'Tools', _('Tools')
        COMPUTE = 'Compute', _('Compute')
        INTEROPERABILITY = 'Interoperability', _('Interoperability')
        TRAINING = 'Training', _('Training')

    # name, description, homepage & coordinator are mandatory
    # null=True is set for coordinator, in case the UserProfile of the coordinator is deleted.
    name = models.CharField(
        max_length=255,
        choices=ElixirPlatformName.choices,
        unique=True,
        help_text="Name of the ELIXIR Platform, e.g. 'Tools'.",
    )

    description = models.TextField(help_text="Short description of the ELIXIR Platform.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the ELIXR Platform.")
    coordinator = models.ForeignKey(
        UserProfile,
        related_name='elixirPlatformCoordinator',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Coordinator of the ELIXIR Platform activities in France.",
    )
    deputies = models.ManyToManyField(
        UserProfile,
        related_name='elixirPlatformDeputies',
        blank=True,
        help_text="Deputy coordinator of the ELIXIR Platform activities in France.",
    )

    def __str__(self):
        """Return the ElixirPlatform model as a string."""
        return self.name


# Organisation field model
# OrganisationField has a many:many relationship to Organisation
class OrganisationField(models.Model):
    """Organisation field model: A broad field that an organisation serves."""

    # field is mandatory
    field = models.CharField(
        max_length=255,
        # choices=OrganisationFieldName.choices, # OrganisationFieldName moved to migration 0058
        unique=True,
        help_text="A broad field that the organisation serves.",
    )

    def __str__(self):
        """Return the OrganisationField model as a string."""
        return self.field


# Organisation model
class Organisation(models.Model):
    """A legal entity involved in research and development, or its support, primarily but not exclusively French organisations directly or indirectly related to bioinformatics."""

    # name, description & homepage are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the organisation.",
        validators=[
            validators.RegexValidator(r'^[a-zA-Z0-9 \-_~]+$', 'Should only contains char such as ^[a-zA-Z0-9\-_~]'),
        ],
    )
    description = models.TextField(help_text="Short description of the organisation.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the organisation.")
    orgid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text="Organisation ID (GRID or ROR ID) of the organisation.",
    )
    fields = models.ManyToManyField(
        OrganisationField,
        blank=True,
        related_name='organisations',
        help_text="A broad field that the organisation serves.",
    )
    city = models.CharField(max_length=255, blank=True, help_text="Nearest city to the organisation.")
    # logo ... TO_DO

    def __str__(self):
        """Return the Organisation model as a string."""
        return self.name


# Community model
class Community(models.Model):
    """Community model: A group of people collaborating on a common scientific or technical topic, including formal ELIXIR  Communities, emerging ELIXIR communities, ELXIR focus groups, IFB communities, and others."""

    # EventType: Controlled vocabulary of types of events.
    class CommunityName(models.TextChoices):
        """Controlled vocabulary of names of communities."""

        # NB: Note "BIOINFO not 3D-BIOINFO" because of Python variable name restrictions.
        BIOINFO = '3D-BioInfo', _('3D-BioInfo')
        GALAXY = 'Galaxy', _('Galaxy')
        INTRINSICALLY_DISORDERED_PROTEINS = 'Intrinsically Disordered Proteins', _('Intrinsically Disordered Proteins')
        MARINE_METAGENOMICS = 'Marine Metagenomics', _('Marine Metagenomics')
        METABOLOMICS = 'Metabolomics', _('Metabolomics')
        MICROBIAL_BIOTECHNOLOGY = 'Microbial Biotechnology', _('Microbial Biotechnology')
        PLANT_SCIENCES = 'Plant Sciences', _('Plant Sciences')
        PROTEOMICS = 'Proteomics', _('Proteomics')
        FEDERATED_HUMAN_DATA = 'Federated Human Data', _('Federated Human Data')
        HUMAN_COPY_NUMBER_VARIATION = 'Human Copy Number Variation', _('Human Copy Number Variation')
        RARE_DISEASES = 'Rare Diseases', _('Rare Diseases')

    # name, description & homepage are mandatory
    # null=True is set for coordinator, in case the UserProfile of the coordinator is deleted.
    name = models.CharField(
        max_length=255, choices=CommunityName.choices, unique=True, help_text="Name of the community, e.g. 'Galaxy'."
    )

    description = models.TextField(help_text="Short description of the community.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the community.")
    organisations = models.ManyToManyField(
        Organisation,
        blank=True,
        related_name='communities',
        help_text="An organisation to which the community is affiliated.",
    )

    class Meta:
        # To overide simply an 's' being appended to "Community" (== "Communitys") in Django admin interface
        verbose_name_plural = "Communities"

    def __str__(self):
        """Return the Community model as a string."""
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
    name = models.CharField(max_length=255, help_text="Full name / title of the event.")
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
        EventTopic, related_name='events', help_text="URIs of EDAM Topic terms describing the scope of the event."
    )
    keywords = models.ManyToManyField(
        EventKeyword, related_name='events', help_text="A keyword (beyond EDAM ontology scope) describing the event."
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
    # sponsoredBy = ... TO_DO
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


# Audience type model
# AudienceType has a many:many relationship to TrainingMaterial
class AudienceType(models.Model):
    """AudienceType model: The education or professional level of the expected audience of the training event or material."""

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


# Audience role model
# AudienceRole has a many:many relationship to TrainingMaterial
class AudienceRole(models.Model):
    """AudienceRole model: The professional roles of the expected audience of the training event or material."""

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


# DifficultyLevelType: Controlled vocabulary for training materials or events describing the required experience and skills of the expected audience.
class DifficultyLevelType(models.TextChoices):
    """Controlled vocabulary for training materials or events describing the required experience and skills of the expected audience."""

    NOVICE = 'Novice', _('Novice')
    INTERMEDIATE = 'Intermediate', _('Intermediate')
    ADVANCED = 'Advanced', _('Advanced')


# Training material model
class Resource(models.Model):
    """Resource model: A computing facility, database, tool or training material provided by a bioinformatics team."""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=255, help_text="Name of the resource.")
    description = models.TextField(help_text="A short description of the resource.")
    communities = models.ManyToManyField(
        Community, blank=True, related_name='resources', help_text="Community which uses the resource."
    )
    elixirPlatforms = models.ManyToManyField(
        ElixirPlatform, blank=True, related_name='resources', help_text="ELIXIR Platform which uses the resource."
    )

    def __str__(self):
        """Return the Resource model as a string."""
        return self.name


class TrainingMaterialLicense(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The professional roles of the expected audience of the training event or material.",
    )

    def __str__(self):
        return self.name


# Training material model
class TrainingMaterial(Resource):
    """Training material model: Digital media such as a presentation or tutorial that can be used for bioinformatics training or teaching."""

    # fileLocation, fileName is mandatory
    # TO-DO:  providedBy
    doi = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text="Unique identier (DOI) of the training material, e.g. a Zenodo DOI.",
    )
    fileLocation = models.URLField(
        max_length=255, help_text="A link to where the training material can be downloaded or accessed."
    )
    fileName = models.CharField(
        max_length=255, help_text="The name of a downloadable file containing the training material."
    )
    topics = models.ManyToManyField(
        EventTopic,
        blank=True,
        related_name='trainingMaterials',
        help_text="URIs of EDAM Topic terms describing the scope of the training material.",
    )
    keywords = models.ManyToManyField(
        EventKeyword,
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
    # providedBy = models.ManyToManyField(BioinformaticsTeam, blank=True, related_name='trainingMaterials', help_text="The bioinformatics team that provides the training material.")
    dateCreation = models.DateField(help_text="Date when the training material was created.")
    dateUpdate = models.DateField(help_text="Date when the training material was updated.")
    license = models.ManyToManyField(
        TrainingMaterialLicense, blank=True, help_text="License under which the training material is made available.",
    )

    def __str__(self):
        """Return the TrainingMaterial model as a string."""
        return self.name


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


# Computing facility model
class ComputingFacility(Resource):
    """Computing facility model: Computing hardware that can be accessed by users for bioinformatics projects."""

    # AccessibillityType: Controlled vocabulary of accessibillity levels of computing facility to end-users.
    class AccessibillityType(models.TextChoices):
        """Controlled vocabulary of accessibillity levels of computing facility to end-users."""

        INTERNAL = 'Internal', _('Internal')
        NATIONAL = 'National', _('National')
        INTERNATIONAL = 'International', _('International')

    # homepage & accessibility are mandatory
    homepage = models.URLField(max_length=255, help_text="URL where the computing facility can be accessed.")
    # TO-DO:  providedBy
    # TO-DO:  team
    accessibility = models.CharField(
        max_length=255,
        choices=AccessibillityType.choices,
        blank=True,
        help_text="Accessibillity of the computing facility to end-users.",
    )
    requestAccount = models.URLField(
        max_length=255, help_text="URL of web page where one can request access to the computing facility."
    )
    termsOfUse = models.URLField(
        max_length=255, help_text="URL where terms of use of the computing facility can be found."
    )
    trainingMaterials = models.ManyToManyField(
        TrainingMaterial,
        blank=True,
        related_name='computingFacilities',
        help_text="Training material for the computing facility.",
    )
    serverDescription = models.CharField(max_length=255, help_text="Description of number and type of servers.")
    storageTb = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Amount of storage (TB) provided by the computing facility.",
        validators=[MinValueValidator(1),],
    )
    cpuCores = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of CPU cores provided by the computing facility.",
        validators=[MinValueValidator(1),],
    )
    ramGb = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="RAM (GB) provided by the computing facility.",
        validators=[MinValueValidator(1),],
    )
    ramPerCoreGb = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="RAM (GB) per CPU core provided by the Platform physical infrastructure.",
        validators=[MinValueValidator(1),],
    )
    cpuHoursYearly = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of CPU hours provided by the computing facility in the last year.",
        validators=[MinValueValidator(1),],
    )
    usersYearly = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of users served by the computing facility in the last year.",
        validators=[MinValueValidator(1),],
    )

    class Meta:
        verbose_name_plural = "Computing facilities"

    def __str__(self):
        """Return the ComputingFacility model as a string."""
        return self.name


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
        null=True,
        on_delete=models.CASCADE,
        help_text="Training event to which the metrics are associated.",
    )

    class Meta:
        verbose_name_plural = "Training event metrics"

    def __str__(self):
        """Return the TrainingEventMetrics model as a string."""
        return self.dateStart.__str__()


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


# Project model
class Project(models.Model):
    """Project model: A scientific or technical project that a French bioinformatics team is involved in."""

    # name, homepage & description are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, help_text="Name of the project.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the project.")
    description = models.TextField(help_text="Description of the project.")
    topics = models.ManyToManyField(
        EventTopic,
        related_name='projects',
        help_text="URIs of EDAM Topic terms describing the expertise of the project.",
    )
    # team  TO-DO
    hostedBy = models.ManyToManyField(
        Organisation, blank=True, related_name='projectsHosts', help_text="Organisation that hosts the project.",
    )
    fundedBy = models.ManyToManyField(
        Organisation, blank=True, related_name='projectsFunders', help_text="Organisation that funds the project.",
    )
    communities = models.ManyToManyField(
        Community, blank=True, related_name='projects', help_text="Community for which the project is relevant.",
    )
    elixirPlatforms = models.ManyToManyField(
        ElixirPlatform,
        blank=True,
        related_name='projects',
        help_text="ELIXIR Platform to which the project is relevant.",
    )
    # uses TO-DO

    def __str__(self):
        """Return the Project model as a string."""
        return self.name


# Team model
class Team(models.Model):
    """Team model: A group of people collaborating on a common project or goals, or organised (formally or informally) into some structure."""

    # name, description, homepage, members & maintainers are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, unique=True, help_text="Name of the team.")
    description = models.TextField(help_text="Description of the team.")
    homepage = models.URLField(max_length=255, null=True, blank=True, help_text="Homepage of the team.")
    expertise = models.ManyToManyField(
        EventTopic, related_name='teams', help_text="URIs of EDAM Topic terms describing the expertise of the team.",
    )
    leader = models.ForeignKey(
        UserProfile, related_name='teamLeader', null=True, on_delete=models.SET_NULL, help_text="Leader of the team.",
    )
    deputies = models.ManyToManyField(
        UserProfile, related_name='teamDeputies', blank=True, help_text="Deputy leader(s) of the team.",
    )
    scientificLeader = models.ForeignKey(
        UserProfile,
        related_name='teamScientificLeader',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Scientific leader of the team.",
    )
    technicalLeader = models.ForeignKey(
        UserProfile,
        related_name='teamTechnicalLeader',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Technical leader of the team.",
    )
    members = models.ManyToManyField(UserProfile, related_name='teamMembers', help_text="Members of the team.",)
    maintainers = models.ManyToManyField(
        UserProfile, related_name='teamMaintainers', help_text="Maintainer(s) of the team metadata in IFB catalogue.",
    )

    def __str__(self):
        """Return the Team model as a string."""
        return self.name


# DOI model
class Doi(models.Model):
    """Digital object identifier model: A digital object identifier (DOI) of a publication or training material."""

    doi = models.CharField(
        max_length=255,
        unique=True,
        help_text="A digital object identifier (DOI) of a publication or training material.",
    )

    def __str__(self):
        """Return the Doi model as a string."""
        return self.doi


# Bioinformatics team model
class BioinformaticsTeam(Team):
    """Bioinformatics team model: A French team whose activities involve the development, deployment, provision, maintenance or support of bioinformatics resources, services or events."""

    # IfbMembershipType: Controlled vocabulary of types of membership bioinformatics teams have to IFB.
    class IfbMembershipType(models.TextChoices):
        """Controlled vocabulary of types of membership bioinformatics teams have to IFB."""

        IFB_PLATFORM = 'IFB platform', _('IFB platform')
        IFB_ASSOCIATED_TEAM = 'IFB-associated team', _('IFB-associated team')
        NOT_A_MEMBER = 'Not a member', _('Not a member')

    # CertificationType: Controlled vocabulary of type of certification of bioinformatics teams.
    class CertificationType(models.TextChoices):
        """Controlled vocabulary of type of certification of bioinformatics teams."""

        CERTIFICATE1 = 'Certificate 1', _('Certificate 1')

    # orgid, ifbMembership & fundedBy are mandatory.
    orgid = models.CharField(max_length=255, unique=True, help_text="Organisation ID (GRID or ROR ID) of the team.",)
    unitId = models.CharField(
        max_length=255,
        blank=True,
        help_text="Unit ID (unique identifier of research or service unit) that the Bioinformatics Team belongs to.",
    )
    address = models.TextField(blank=True, help_text="Postal address of the bioinformatics team.")
    # TO-DO logo
    fields = models.ManyToManyField(
        OrganisationField,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="A broad field that the bioinformatics team serves.",
    )
    topics = models.ManyToManyField(
        EventTopic,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="URIs of EDAM Topic terms describing the bioinformatics team.",
    )
    keywords = models.ManyToManyField(
        EventKeyword,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="A keyword (beyond EDAM ontology scope) describing the bioinformatics team.",
    )
    ifbMembership = models.CharField(
        max_length=255,
        choices=IfbMembershipType.choices,
        help_text="Type of membership the bioinformatics team has to IFB.",
    )
    affiliatedWith = models.ManyToManyField(
        Organisation,
        blank=True,
        related_name='bioinformaticsTeamsAffiliatedWith',
        help_text="Organisation(s) to which the bioinformatics team is affiliated.",
    )
    platforms = models.ManyToManyField(
        ElixirPlatform,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="ELIXIR Platform(s) in which the bioinformatics team is involved.",
    )
    communities = models.ManyToManyField(
        Community,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="Communities in which the bioinformatics team is involved.",
    )
    projects = models.ManyToManyField(
        Project,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="Project(s) that the bioinformatics team is involved with, supports or hosts.",
    )
    fundedBy = models.ManyToManyField(
        Organisation,
        related_name='bioinformaticsTeamsFundedBy',
        help_text="Organisation(s) that funds the bioinformatics team.",
    )
    publications = models.ManyToManyField(
        Doi, related_name='bioinformaticsTeams', blank=True, help_text="Publication(s) that describe the team.",
    )
    certification = models.CharField(
        max_length=255,
        blank=True,
        choices=CertificationType.choices,
        help_text="Certification (e.g. ISO) of the bioinformatics team.",
    )
