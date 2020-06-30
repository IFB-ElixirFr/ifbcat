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
from django.utils.translation import gettext_lazy as _

# Manager for custom user profile model
class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    # Function that Django CLI will use when creating users
    # password=None means that if a password is not set it wil default to None,
    # preventing authentication with the user until a password is set.
    def create_user(self, firstname, lastname, email, orcidid, homepage, password=None):
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
    def create_superuser(self, firstname, lastname, email, orcidid, homepage, password):
        """Create a new superuser profile"""

        user = self.create_user(password, firstname, lastname, email, orcid, homepage)

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
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    orcidid = models.CharField(max_length=255, null=True, blank=True, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    homepage = models.URLField(max_length=255, null=True, blank=True)
    # expertise = ... TO_DO

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

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
    # Could set the field to NULL instead (if we wanted to preserve the news items)
    user_profile = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
    )

    # news_text and created_on are mandatory
    # "auto_now_add=True" means that the date/time stamp gets added automatically when the item is created.
    news_text = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the NewsItem model as a string."""
        return self.news_text


# Event model
class Event(models.Model):
    """Event model: A scheduled scholarly gathering such as workshop, conference, symposium, training or open project meeting of relevance to bioinformatics."""

    # Controlled vocabularies
    # See https://docs.djangoproject.com/en/dev/ref/models/fields/#enumeration-types
    # The enums support internatonalization (using the '_' shorthand convention for gettext_lazy() function)
    # See https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#internationalization-in-python-code

    # EventType: Controlled vocabulary of types of events.
    class EventType(models.TextChoices):
        WORKSHOP = 'WO', _('Workshop')
        TRAINING_COURSE = 'TR', _('Training course')
        MEETING = 'ME', _('Meeting')
        CONFERENCE = 'CO', _('Conference')


    # name, description, homepage, accessibility, contactName and contactEmail are mandatory
    name = models.CharField(max_length=255)
    shortName = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    homepage = models.URLField(max_length=255, null=True, blank=True)
    type = models.CharField(
        max_length=2,
        choices=EventType.choices,
        blank = True
    )

    # dates = ... TO_DO
    venue = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255,blank=True)
    onlineOnly = models.BooleanField(null=True, blank=True)
    # cost = ... TO_DO
    # topic = ... TO_DO
    # keyword = ... TO_DO
    # prerequisite = ... TO_DO
    # accessibility = ... TO_DO
    accessibilityNote = models.CharField(max_length=255, blank=True)
    maxParticipants = models.PositiveSmallIntegerField(null=True, blank=True)
    contactName = models.CharField(max_length=255)
    contactEmail = models.EmailField()
    # contactId = ... TO_DO
    market = models.CharField(max_length=255, blank=True)
    # elixirPlatform = ... TO_DO
    # community = ... TO_DO
    # hostedBy = ... TO_DO
    # organisedBy = ... TO_DO
    # sponsoredBy = ... TO_DO
    # logo = ... TO_DO
