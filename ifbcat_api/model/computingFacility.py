# Imports
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.resource import Resource


# from ifbcat_api.model.team import Team


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
    providedBy = models.ForeignKey(
        'ifbcat_api.Team',
        null=True,
        on_delete=models.SET_NULL,
        help_text="The team which is maintaining the computing facility.",
    )
    accessibility = models.CharField(
        max_length=255,
        choices=AccessibillityType.choices,
        help_text="Accessibillity of the computing facility to end-users.",
    )
    requestAccount = models.URLField(
        max_length=255, blank=True, help_text="URL of web page where one can request access to the computing facility."
    )
    termsOfUse = models.URLField(
        max_length=255, blank=True, help_text="URL where terms of use of the computing facility can be found."
    )
    trainingMaterials = models.ManyToManyField(
        'TrainingMaterial',
        blank=True,
        related_name='computingFacilities',
        help_text="Training material for the computing facility.",
    )
    storageTb = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Amount of storage (TB) provided by the computing facility.",
        validators=[
            MinValueValidator(1),
        ],
    )
    cpuCores = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of CPU cores provided by the computing facility.",
        validators=[
            MinValueValidator(1),
        ],
    )
    ramGb = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="RAM (GB) provided by the computing facility.",
        validators=[
            MinValueValidator(1),
        ],
    )
    ramPerCoreGb = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="RAM (GB) per CPU core provided by the Platform physical infrastructure.",
        validators=[
            MinValueValidator(1),
        ],
    )
    cpuHoursYearly = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of CPU hours provided by the computing facility in the last year.",
        validators=[
            MinValueValidator(1),
        ],
    )
    usersYearly = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of users served by the computing facility in the last year.",
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name_plural = "Computing facilities"

    def __str__(self):
        """Return the ComputingFacility model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.UserCanAddNew
            | permissions.ReadWriteByTeamLeader
            | permissions.ReadWriteByTeamDeputies
            | permissions.ReadWriteByTeamMaintainers
            | permissions.ReadWriteByCurator
            | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )
