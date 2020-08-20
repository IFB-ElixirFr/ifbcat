# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from ifbcatsandbox_api.model.resource import *
from ifbcatsandbox_api.model.team import *
from ifbcatsandbox_api.model.trainingMaterial import *
from ifbcatsandbox_api.model.bioinformaticsTeam import *


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

    # Quotes around 'BioinformaticsTeam' are essential as a workound to a circular dependency:
    # ''ComputingFacility'' includes a ``BioinformaticsTeam`` field which  includes a ``Project``
    # field which includes a ''ComputingFacility'' field.
    # See https://stackoverflow.com/questions/7684408/django-cannot-import-name-x
    # See https://docs.djangoproject.com/en/dev/ref/models/fields/#foreignkey

    providedBy = models.ForeignKey(
        'BioinformaticsTeam',
        related_name='computingFacilityProvidedBy',
        null=True,
        on_delete=models.SET_NULL,
        help_text="The bioinformatics team that provides the computing facility.",
    )
    team = models.ForeignKey(
        Team,
        related_name='computingFacilityTeam',
        null=True,
        on_delete=models.SET_NULL,
        help_text="The team which is maintaining the computing facility.",
    )
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
