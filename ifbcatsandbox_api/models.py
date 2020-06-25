# Imports
# AbstractBaseUser and PermissionsMixin are the base classes used when customising the Django user model
# BaseUserManager is the default user manager that comes with Django
# see https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#auth-custom-user
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager


# Manager for custom user profile model
class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    # Function that Django CLI will use when creating users
    # password=None means that if a password is not set it wil default to None,
    # preventing authentication with the user until a password is set.
    def create_user(self, email, firstname, lastname, password=None):
        """Create a new user profile"""
        if not email:
            raise ValueError('Users must have an email address.')
        if not firstname:
            raise ValueError('Users must have a first name.')
        if not lastname:
            raise ValueError('Users must have a last name.')

        # Normalize the email address (makes the 2nd part of the addrss all lowercase)
        email = self.normalize_email(email)
        user = self.model(email=email, firstname=firstname, lastname=lastname)

        # Set password will encrypt the provided password - good practice to do so!
        # Even thoough there's only one database, it's good practice to name the databaes anyway, using:
        # user.save(using=self._db)
        user.set_password(password)
        user.save(using=self._db)

        return user

    # Function for creating super-users
    # NB. all superusers must have a password, hence no "password=Nane"
    def create_superuser(self, email, firstname, lastname, password):
        """Create a new superuser profile"""
        user = self.create_user(email, firstname, lastname, password)

        # .is_superuser and is_staff come from PermissionsMixin
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

# Custom user profile model
#
# User profiles are set by default to be active (is_active = ...) and are not staff (is_staff = ...)
# NB. staff users have access to Django admin etc.
class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system."""
    email = models.EmailField(max_length=255, unique=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)

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
