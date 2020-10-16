# Imports
# BaseUserManager is the default user manager that comes with Django
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from ifbcat_api.model.misc import Topic
from ifbcat_api.validators import validate_orcid


class UserProfileManager(BaseUserManager):
    """Manager for custom user profiles model
    For more on user models with authentication see https://github.com/django/django/blob/stable/3.0.x/django/contrib/auth/models.py#L131-L158
    """

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
        user = self.model(
            firstname=firstname,
            lastname=lastname,
            email=email,
            orcidid=orcidid,
            homepage=homepage,
        )

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
    orcidid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text="ORCID ID of a person (IFB catalogue user).",
        validators=[
            validate_orcid,
        ],
    )
    email = models.EmailField(max_length=255, unique=True, help_text="Email address of a person (IFB catalogue user).")
    homepage = models.URLField(
        max_length=255, null=True, blank=True, help_text="Homepage of a person (IFB catalogue user)."
    )
    expertise = models.ManyToManyField(
        Topic,
        related_name='userprofiles',
        blank=True,
        help_text="URIs of EDAM Topic terms describing the expertise of a person (IFB catalogue user).",
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
