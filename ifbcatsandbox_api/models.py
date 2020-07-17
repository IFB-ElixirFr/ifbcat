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
            password=password,
            firstname=firstname,
            lastname=lastname,
            email=email,
            orcidid=orcidid,
            homepage=homepage,
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
    orcidid = models.CharField(max_length=255, null=True, blank=True, unique=True, help_text="ORCID ID of a person (IFB catalogue user).")
    email = models.EmailField(max_length=255, unique=True, help_text="Email address of a person (IFB catalogue user).")
    homepage = models.URLField(max_length=255, null=True, blank=True, help_text="Homepage of a person (IFB catalogue user).")
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
    user_profile = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
    )

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

    # "on_delete=models.NULL" means that the EventKeyword is not deleted if the user profile is deleted.
    # "null=True" is required in case a user profile IS deleted.

    #user_profile = models.ForeignKey(
    #settings.AUTH_USER_MODEL,
    #on_delete=models.SET_NULL,
    #null=True
    #)

    # keyword is mandatory
    # For "event":
    #    "null=True" is required in case an event is deleted.
    #    "blank=True" is required to allow registration of keywords independent of events.
    # event = models.ForeignKey(Event, related_name='keywords', blank=True, null=True, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=255, unique=True, help_text="A keyword (beyond EDAM ontology scope) describing the event.")

    def __str__(self):
        """Return the EventKeyword model as a string."""
        return self.keyword



# Event prerequisite model
# Prerequisites have a many:one relationship to Event
# Same code as for EventKeyword
class EventPrerequisite(models.Model):
    """Event prerequisite model: A skill which the audience should (ideally) possess to get the most out of the event, e.g. "Python"."""

    #user_profile = models.ForeignKey(
    #settings.AUTH_USER_MODEL,
    #on_delete=models.SET_NULL,
    #null=True
    #)

    # prerequisite is mandatory
    # event = models.ForeignKey(Event, related_name='prerequisites', blank=True, null=True, on_delete=models.CASCADE)
    prerequisite = models.CharField(max_length=255, unique=True, help_text="A skill which the audience should (ideally) possess to get the most out of the event, e.g. 'Python'.")

    def __str__(self):
        """Return the EventPrerequisite model as a string."""
        return self.prerequisite


# Event topic model
# Event topic has a many:many relationship to Event
class EventTopic(models.Model):
    """Event topic model: URI of EDAM Topic term describing the scope of the event."""

    # topic is mandatory
    topic = models.CharField(max_length=255, unique=True, help_text="URI of EDAM Topic term describing the scope of the event.")

    def __str__(self):
        """Return the EventTopic model as a string."""
        return self.topic



# Event cost model
# Event cost has a many:many relationship to Event
class EventCost(models.Model):
    """Event cost model: Monetary cost to attend the event, e.g. 'Free to academics'."""

    # CostType: Controlled vocabulary of monetary costs to attend an event.
    class CostType(models.TextChoices):
        # FREE = 'FR', _('Free')
        # FREE_TO_ACADEMICS = 'FA', _('Free to academics')
        # CONCESSIONS_AVAILABLE = 'CO', _('Concessions available')
        FREE = 'Free', _('Free')
        FREE_TO_ACADEMICS = 'Free to academics', _('Free to academics')
        PRICED = 'Priced', _('Priced')
        CONCESSIONS_AVAILABLE = 'Concessions available', _('Concessions available')


    # cost is mandatory
    cost = models.CharField(
        max_length=255,
        choices=CostType.choices,
        unique=True,
        help_text="Monetary cost to attend the event, e.g. 'Free to academics'.")

    def __str__(self):
        """Return the EventCost model as a string."""
        return self.cost




# Event model
class Event(models.Model):
    """Event model: A scheduled scholarly gathering such as workshop, conference, symposium, training or open project meeting of relevance to bioinformatics."""

    # "on_delete=models.NULL" means that the Event is not deleted if the user profile is deleted.
    # "null=True" is required in case a user profile IS deleted.
    user_profile = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True
    )

    # Controlled vocabularies
    # See https://docs.djangoproject.com/en/dev/ref/models/fields/#enumeration-types
    # The enums support internatonalization (using the '_' shorthand convention for gettext_lazy() function)
    # See https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#internationalization-in-python-code

    # EventType: Controlled vocabulary of types of events.
    # Not using both short-form names and human-readable labels, because of issue:
    # see https://github.com/joncison/ifbcat-sandbox/pull/9
    class EventType(models.TextChoices):
        # WORKSHOP = 'WO', _('Workshop')
        # TRAINING_COURSE = 'TR', _('Training course')
        # MEETING = 'ME', _('Meeting')
        # CONFERENCE = 'CO', _('Conference')
        WORKSHOP = 'Workshop', _('Workshop')
        TRAINING_COURSE = 'Training course', _('Training course')
        MEETING = 'Meeting', _('Meeting')
        CONFERENCE = 'Conference', _('Conference')


    # EventAccessibilityType: Controlled vocabulary for whether an event is public or private.
    class EventAccessibilityType(models.TextChoices):
        # PUBLIC = 'PU', _('Public')
        # PRIVATE = 'PR', _('Private')
        PUBLIC = 'Public', _('Public')
        PRIVATE = 'Private', _('Private')

    # name, description, homepage, accessibility, contactName and contactEmail are mandatory
    name = models.CharField(max_length=255, help_text="Full name / title of the event.")
    shortName = models.CharField(max_length=255, blank=True, help_text="Short name (or acronym) of the event.")
    description = models.TextField(help_text="Description of the event.")
    homepage = models.URLField(max_length=255, null=True, blank=True, help_text="URL of event homepage.")

    # NB: max_length is mandatory, but is ignored by sqlite3, see https://github.com/joncison/ifbcat-sandbox/pull/9
    type = models.CharField(
        max_length=255,
        choices=EventType.choices,
        blank=True,
        help_text="The type of event e.g. 'Training course'."
    )

    # dates: handled by a ForeignKey relationship defined in EventDate (many:one EventDate:Event)
    venue = models.TextField(blank=True, help_text="The address of the venue where the event will be held.")
    city = models.CharField(max_length=255, blank=True, help_text="The nearest city to where the event will be held.")
    country = models.CharField(max_length=255,blank=True, help_text="The country where the event will be held.")
    onlineOnly = models.BooleanField(null=True, blank=True, help_text="Whether the event is hosted online only.")
    costs = models.ManyToManyField(EventCost, related_name='events', help_text="Monetary cost to attend the event, e.g. 'Free to academics'.")
    topics = models.ManyToManyField(EventTopic, related_name='events', help_text="URI of EDAM Topic term describing the scope of the event.")
    keywords = models.ManyToManyField(EventKeyword, related_name='events', help_text="A keyword (beyond EDAM ontology scope) describing the event.")
    prerequisites = models.ManyToManyField(EventPrerequisite, related_name='events', help_text="A skill which the audience should (ideally) possess to get the most out of the event, e.g. 'Python'.")
    accessibility = models.CharField(
        max_length=255,
        choices=EventAccessibilityType.choices,
        blank=True,
        help_text="Whether the event is public or private."
    )
    accessibilityNote = models.CharField(max_length=255, blank=True, help_text="Comment about the audience a private event is open to and tailored for.")
    maxParticipants = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants to the event.",
        validators=[MinValueValidator(1),],
    )
    contactName = models.CharField(max_length=255, help_text="Name of person to contact about the event.")
    contactEmail = models.EmailField(help_text="Email of person to contact about the event.")
    # contactId = ... TO_DO
    market = models.CharField(max_length=255, blank=True, help_text="Geographical area which is the focus of event marketing efforts.")
    # elixirPlatform = ... TO_DO
    # community = ... TO_DO
    # hostedBy = ... TO_DO
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
    dateEnd = models.DateField(blank=True, help_text="The end date of the event.")
    timeStart = models.TimeField(blank=True, help_text="The start time of the event.")
    timeEnd = models.TimeField(blank=True, help_text="The end time of the event.")

    event = models.ForeignKey(Event, related_name='dates', on_delete=models.CASCADE)

    def __str__(self):
        """Return the EventDate model as a string."""
        return self.dateStart.__str__()
