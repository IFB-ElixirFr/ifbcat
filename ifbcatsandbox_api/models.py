# Imports
# AbstractBaseUser and PermissionsMixin are the base classes used when customising the Django user model
# BaseUserManager is the default user manager that comes with Django
# see https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#auth-custom-user
# "settings" is for retrieving settings from settings.py file (project file)
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.conf import settings


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
# NB. we cannot have "unique=True" for orcidid, because these are not mandatory ()
class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system."""
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    orcidid = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    homepage = models.URLField(max_length=255, null=True, blank=True)

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

    # "auto_now_add=True" means that the date/time stamp gets added automatically when the item is created.
    news_text = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the NewsItem model as a string."""
        return self.news_text
