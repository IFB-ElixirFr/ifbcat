# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _


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