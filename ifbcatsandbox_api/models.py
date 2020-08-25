# Imports
# AbstractBaseUser and PermissionsMixin are the base classes used when customising the Django user model
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

# from django.core import validators
# from django.db import models
# from django.conf import settings

# from django.core.validators import MinValueValidator
# from django.utils.translation import gettext_lazy as _
# from django.core.validators import MinValueValidator

from .model.userProfile import *
from .model.event import *
from .model.elixirPlatform import *
from .model.organisation import *
from .model.community import *
from .model.resource import *
from .model.trainingMaterial import *
from .model.team import *
from .model.bioinformaticsTeam import *
from .model.computingFacility import *
from .model.project import *
from .model.trainingEvent import *
from .model.service import *
from .model.misc import *
