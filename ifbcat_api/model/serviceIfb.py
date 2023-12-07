from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.team import Team
from ifbcat_api.validators import validate_can_be_looked_up


class AbstractControlledVocabulary(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(
        max_length=255,
        unique=True,
        validators=[
            validate_can_be_looked_up,
        ],
    )

    def __str__(self):
        """Return the Keyword model as a string."""
        return self.name

    def clean_fields(self, exclude=None):
        super().clean_fields()
        if exclude is not None and "keyword" in exclude:
            return
        qs = self.__class__.objects.filter(name__unaccent__iexact=self.name).filter(~Q(pk=self.pk))
        if qs.exists():
            raise ValidationError(
                f"{self._meta.verbose_name} \"{self.keyword}\" already exists as \"{qs.get().keyword}\""
            )

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly | permissions.ReadWriteBySuperuser | permissions.ReadWriteByCurator,
            IsAuthenticatedOrReadOnly,
        )


class ServiceDomain(AbstractControlledVocabulary):
    pass


class KindOfAnalysis(AbstractControlledVocabulary):
    pass


class LifeScienceCommunity(AbstractControlledVocabulary):
    pass


class ServiceCategory(AbstractControlledVocabulary):
    pass


class Service(models.Model):
    class Meta:
        unique_together = (('team', 'domain', 'analysis'),)

    class TrainingType(models.TextChoices):
        NO = 'No', _('No')
        RECURRENT = 'Recurrent', _('Recurrent')
        CUSTOM = 'Custom', _('Custom')

    class StandardAndOrCustom(models.TextChoices):
        NO = 'No', _('No')
        STANDARD = 'Standard', _('Standard')
        CUSTOM = 'Custom', _('Custom')
        BOTH = 'both', _('Standard and custom')

    comments = models.TextField(
        blank=True,
        null=True,
    )
    training = models.CharField(
        choices=TrainingType.choices,
        default=TrainingType.NO,
        max_length=10,
        null=False,
        blank=False,
    )
    mentoring = models.BooleanField(
        default=False,
    )

    collaboration = models.CharField(
        choices=StandardAndOrCustom.choices,
        default=StandardAndOrCustom.NO,
        max_length=10,
        null=False,
        blank=False,
    )

    prestation = models.CharField(
        choices=StandardAndOrCustom.choices,
        default=StandardAndOrCustom.NO,
        max_length=10,
        null=False,
        blank=False,
    )

    team = models.ForeignKey(
        Team,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text="The bioinformatics team(s) that provides this service.",
        related_name="services",
    )
    domain = models.ForeignKey(
        ServiceDomain,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text="Domain of the service.",
    )
    analysis = models.ForeignKey(
        KindOfAnalysis,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        help_text="Kind of analysis proposed.",
        verbose_name='Action',
    )
    communities = models.ManyToManyField(
        LifeScienceCommunity,
        blank=True,
        help_text="Biological community concerned. Example: Human, plants, animals, micro-organism, health, ...",
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        help_text='Category of service it belongs.',
    )

    def __str__(self):
        return f'[{self.domain}] {self.analysis} by {self.team} ({", ".join(self.communities.all())})'

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.ReadWriteByTeamLeaders
            | permissions.ReadWriteByTeamDeputies
            | permissions.ReadWriteByTeamMaintainers
            | permissions.ReadWriteByCurator
            | permissions.ReadWriteBySuperEditor
            | permissions.UserCanAddNew,
            IsAuthenticatedOrReadOnly,
        )
