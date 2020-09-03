# Imports
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


# Topic model
from ifbcatsandbox_api.validators import validate_edam_topic


class Topic(models.Model):
    """Event topic model: URI of EDAM Topic term describing scope or expertise."""

    # topic is mandatory
    topic = models.CharField(
        max_length=255,
        unique=True,
        help_text="URI of EDAM Topic term describing scope or expertise.",
        validators=[validate_edam_topic,],
    )

    def __str__(self):
        """Return the Topic model as a string."""
        return self.topic


# Keyword model
class Keyword(models.Model):
    """Keyword model: A keyword (beyond EDAM ontology scope)."""

    keyword = models.CharField(
        max_length=255,
        unique=True,
        help_text="A keyword (beyond EDAM ontology scope).",
        validators=[RegexValidator(r'^[a-zA-Z0-9 \-_~]+$', 'Should only contains char such as ^[a-zA-Z0-9\-_~]'),],
    )

    def __str__(self):
        """Return the Keyword model as a string."""
        return self.keyword

    def clean_fields(self, exclude=None):
        super().clean_fields()
        if exclude is not None and "keyword" in exclude:
            return
        if Keyword.objects.filter(keyword__iexact=self.keyword).filter(~Q(pk=self.pk)).exists():
            raise ValidationError(
                "Keyword \"%s\" already exists as \"%s\""
                % (self.keyword, Keyword.objects.filter(keyword__iexact=self.keyword).get().keyword)
            )


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


# Field model
class Field(models.Model):
    """Field model: A broad field that an organisation or bioinformatics team serves."""

    # field is mandatory
    field = models.CharField(
        max_length=255,
        # choices=OrganisationFieldName.choices, # OrganisationFieldName moved to migration 0058
        unique=True,
        help_text="A broad field that the organisation or bioinformatics serves.",
    )

    def __str__(self):
        """Return the Field model as a string."""
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
