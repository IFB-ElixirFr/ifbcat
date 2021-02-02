"""
Django settings for ifbcat project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import logging
import os

from decouple import config, UndefinedValueError

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from ifbcat import db_finder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', '#1eg!-*r&1*y8*s9!g^!if!-(1&11k0%*7b$-jwgv!7u!ae7wt')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', 'true').lower() == 'true'

try:
    ALLOWED_HOSTS = [s.strip() for s in config('ALLOWED_HOSTS', '127.0.0.1').split(',')]
except UndefinedValueError:
    print('WARNING: ALLOWED_HOSTS not found. Declare it as environment variable for production environments.')

# Application definition
#
# Installed apps include
# 1) external dependencies (installed via requirements.txt)
# 2) apps from the Django REST framework
# 3) our ifbcat_api app

INSTALLED_APPS = [
    'jazzmin_patch',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_templates_patch',
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'django_better_admin_arrayfield',
    'ifbcat_api',
    'django.contrib.postgres',
]

# INSTALLED_APPS.append('django_extensions')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'ifbcat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ifbcat.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if os.environ.get('POSTGRES_PASSWORD', '') == '':
    DATABASES_HOST = db_finder.get_db_ip()
else:
    DATABASES_HOST = 'db'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': DATABASES_HOST,
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Configure Django to use our custom user model for authentication and user registration
AUTH_USER_MODEL = 'ifbcat_api.UserProfile'

REST_FRAMEWORK = {
    # authentication_classes sets how user is authenticated.
    # Token authentication works by generating a random token when the user logs in,
    # which is passed to every request that needs to be authenticated.
    # authentication_classes is created as tuple below - more than one type of authentication can be added.
    # For more info, seee https://security.stackexchange.com/questions/81756/session-authentication-vs-token-authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # allows to put used within the browser
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'ifbcat_api.filters.DjangoFilterAutoSubsetBackend',
    ),
}
# From https://gist.github.com/davewongillies/6897161#gistcomment-3017261
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

################################################################################
# Log level
################################################################################
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO' if DEBUG else 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

################################################################################
# JAZZMIN CONFIGURATION
################################################################################
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    # "brand_colour": "navbar-white navbar-light",
    "accent": "accent-primary",
    "navbar": "navbar-gray-dark navbar-dark",
    # "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    # "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "actions_sticky_top": True,
}
JAZZMIN_SETTINGS = {
    # title of the window
    "site_title": "IFB Catalogue",
    #
    # Title on the brand, and the login screen (19 chars max)
    "site_header": "IFB Catalogue",
    #
    # square logo to use for your site, must be present in static files, used for favicon and brand on top left
    "site_logo": "/img/logo-ifb_small.png",
    #
    # Welcome text on the login screen
    "welcome_sign": "Welcome to the IFB Resources Catalogue",
    # Copyright on the footer
    # "copyright": "Acme Library Ltd",
    #
    # The model admin to search from the search bar, search bar omitted if excluded
    # "search_model": "ifbcat_api.Tool",
    #
    ############
    # Top Menu #
    ############
    #
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://github.com/IFB-ElixirFr/ifbcat/issues", "new_window": True},
        {"model": "ifbcat_api.UserProfile"},
        {"model": "ifbcat_api.Event"},
        {"model": "ifbcat_api.BioinformaticsTeam"},
        {"app": "ifbcat_api"},
    ],
    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free
    # for a list of icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "authtoken.Token": "fas fa-key",
        "ifbcat_api.AudienceRole": "fas fa-circle",
        "ifbcat_api.AudienceType": "fas fa-circle",
        "ifbcat_api.BioinformaticsTeam": "fas fa-users",
        "ifbcat_api.Certification": "fas fa-circle",
        "ifbcat_api.Collection": "fas fa-circle",
        "ifbcat_api.Community": "fas fa-broadcast-tower",
        "ifbcat_api.ComputingFacility": "fas fa-circle",
        "ifbcat_api.Doi": "fas fa-file-alt",
        "ifbcat_api.ElixirPlatform": "fas fa-circle",
        "ifbcat_api.EventCost": "fas fa-circle",
        "ifbcat_api.EventDate": "fas fa-circle",
        "ifbcat_api.EventPrerequisite": "fas fa-circle",
        "ifbcat_api.EventSponsor": "fas fa-circle",
        "ifbcat_api.Event": "fas fa-calendar-alt",
        "ifbcat_api.Field": "fas fa-circle",
        "ifbcat_api.Keyword": "fas fa-circle",
        "ifbcat_api.OperatingSystem": "fas fa-robot",
        "ifbcat_api.Organisation": "fas fa-sitemap",
        "ifbcat_api.Project": "fas fa-project-diagram",
        "ifbcat_api.ServiceSubmission": "fas fa-circle",
        "ifbcat_api.Service": "fas fa-circle",
        "ifbcat_api.Team": "fas fa-users",
        "ifbcat_api.ToolCredit": "fas fa-circle",
        "ifbcat_api.ToolType": "fas fa-circle",
        "ifbcat_api.Tool": "fas fa-tools",
        "ifbcat_api.Topic": "fas fa-circle",
        "ifbcat_api.Trainer": "fas fa-chalkboard-teacher",
        "ifbcat_api.TrainingEventMetrics": "fas fa-circle",
        "ifbcat_api.TrainingEvent": "fas fa-school",
        "ifbcat_api.TrainingMaterial": "fas fa-book",
        "ifbcat_api.TypeRole": "fas fa-circle",
        "ifbcat_api.UserProfile": "fas fa-user",
    },
    #
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [
        "ifbcat_api",
        "authtoken",
        "auth",
    ],
    #
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": "/css/ifbcat_admin.css",
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,
    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "ifbcat_api.UserProfile": "single",
    },
}
if config('USE_IFB_THEME', True, cast=bool):
    JAZZMIN_UI_TWEAKS.update(
        {
            "brand_colour": "navbar-white navbar-light",
            "navbar": "navbar-white navbar-light",
            "sidebar": "sidebar-light-primary",
            "sidebar_fixed": False,
        }
    )
    JAZZMIN_SETTINGS.update(
        {
            "show_ui_builder": False,
        }
    )

################################################################################
