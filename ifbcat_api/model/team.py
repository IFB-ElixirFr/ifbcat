# Imports
import functools

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import When, Q, Case, Value, BooleanField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.certification import Certification
from ifbcat_api.model.community import Community
from ifbcat_api.model.elixirPlatform import ElixirPlatform
from ifbcat_api.model.misc import Keyword, Field, Topic, Doi, WithGridIdOrRORId
from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.project import Project
from ifbcat_api.model.tool.tool import Tool
from ifbcat_api.model.userProfile import UserProfile
from ifbcat_api.validators import validate_can_be_looked_up


class Team(WithGridIdOrRORId, models.Model):
    """Team model: A group of people collaborating on a common project or goals, or organised (formally or informally) into some structure."""

    # CertificationType: Controlled vocabulary of type of certification of bioinformatics teams.
    class CertificationType(models.TextChoices):
        """Controlled vocabulary of type of certification of teams."""

        CERTIFICATE1 = 'Certificate 1', _('Certificate 1')

    # name, description, homepage, members & maintainers are mandatory
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the team.",
        validators=[
            validate_can_be_looked_up,
        ],
    )
    description = models.TextField(help_text="Description of the team.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the team.")
    logo_url = models.URLField(max_length=512, help_text="URL of logo of the team.", blank=True, null=True)
    fields = models.ManyToManyField(
        Field,
        blank=True,
        related_name='teamsFields',
        help_text="A broad field that the team serves.",
    )
    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        related_name='teamsKeywords',
        help_text="A keyword (beyond EDAM ontology scope) describing the team.",
    )
    expertise = models.ManyToManyField(
        Topic,
        related_name='teamsExpertise',
        blank=True,
        help_text='Required for IFB platform and associated team. Please enter here one or several keywords '
        'describing the general and specific expertises of the team. Please note that individual '
        'expertises will also be documented in the "members" tab.',
    )
    linkCovid19 = models.TextField(
        blank=True, help_text="Describe the ways your team contributes to resources related to Covid-19."
    )
    leaders = models.ManyToManyField(
        UserProfile,
        related_name='teamsLeaders',
        blank=True,
        help_text="Leader(s) of the team.",
    )
    deputies = models.ManyToManyField(
        UserProfile,
        related_name='teamsDeputies',
        help_text="Deputy leader(s) of the team.",
        blank=True,
    )
    scientificLeaders = models.ManyToManyField(
        UserProfile,
        related_name='teamsScientificLeaders',
        help_text="Scientific leader(s) of the team.",
        blank=True,
    )
    technicalLeaders = models.ManyToManyField(
        UserProfile,
        related_name='teamsTechnicalLeaders',
        help_text="Technical leader(s) of the team.",
        blank=True,
    )
    members = models.ManyToManyField(
        UserProfile,
        related_name='teamsMembers',
        help_text="Members of the team.",
    )
    maintainers = models.ManyToManyField(
        UserProfile,
        related_name='teamsMaintainers',
        help_text="A maintainer of a team in the IFB catalogue can edit its metadata.",
        blank=True,
    )
    unitId = models.CharField(
        max_length=255,
        blank=True,
        help_text="Unit ID (unique identifier of research or service unit) that the Team belongs to.",
    )
    address = models.TextField(blank=True, help_text="Postal address of the team.")
    city = models.CharField(max_length=255, blank=True, help_text="City where the team is located.")
    country = models.CharField(max_length=255, blank=True, help_text="country where the team is located.")
    communities = models.ManyToManyField(
        Community,
        blank=True,
        related_name='teamsCommunities',
        help_text="Communities in which the bioinformatics team is involved.",
    )
    projects = models.ManyToManyField(
        Project,
        blank=True,
        related_name='teamsProjects',
        help_text="Project(s) that the team is involved with, supports or hosts.",
    )
    fundedBy = models.ManyToManyField(
        Organisation,
        related_name='teamsFunders',
        help_text="Organisation(s) that funds the team.",
    )
    publications = models.ManyToManyField(
        Doi,
        related_name='teamsPublications',
        blank=True,
        help_text="Publication(s) that describe the team.",
    )
    certifications = models.ManyToManyField(
        Certification,
        related_name='teamsCertifications',
        blank=True,
        help_text="Certification(s) possessed by the team.",
    )
    affiliatedWith = models.ManyToManyField(
        Organisation,
        blank=True,
        related_name='teamsAffiliatedWith',
        help_text="Organisation(s) to which the team is affiliated.",
    )
    tools = models.ManyToManyField(
        Tool,
        blank=True,
        related_name='teams',
        help_text="Tool(s) developped by the team.",
    )
    closing_date = models.DateField(
        help_text="After this date the team is closed. Leave blank if the team is still open/active.",
        blank=True,
        null=True,
        default=None,
    )

    #############################
    # BioTeam related attributes
    #############################

    class IfbMembershipType(models.TextChoices):
        MEMBER_PLATFORM = 'Member platform', _('Member platform')
        CONTRIBUTING_TEAM = 'Contributing platform', _('Contributing platform')
        ASSOCIATED_TEAM = 'Associated Team', _('Associated Team')
        NO_MEMBERSHIP = 'None', _('None')

    ifbMembership = models.CharField(
        max_length=255,
        choices=IfbMembershipType.choices,
        help_text="Type of membership the bioinformatics team has to IFB.",
        default=IfbMembershipType.NO_MEMBERSHIP,
    )
    platforms = models.ManyToManyField(
        ElixirPlatform,
        blank=True,
        related_name='teamsPlatforms',
        help_text="ELIXIR Platform(s) in which the bioinformatics team is involved.",
    )

    def __str__(self):
        """Return the Team model as a string."""
        return self.name

    @classmethod
    def annotate_is_active(cls, qs=None):
        if qs is None:
            qs = cls.objects
        return qs.annotate(
            is_active=Case(
                When(Q(closing_date__lt=timezone.now()), then=Value(False)),
                default=Value(True),
                output_field=BooleanField(),
            )
        )

    @classmethod
    def get_permission_classes(cls):
        return (
            functools.reduce(lambda a, b: a | b, cls.get_edition_permission_classes()),
            IsAuthenticatedOrReadOnly,
        )

    @classmethod
    def get_edition_permission_classes(cls):
        return (
            permissions.ReadOnly,
            permissions.ReadWriteByLeader,
            permissions.ReadWriteByDeputies,
            permissions.ReadWriteByMaintainers,
            permissions.ReadWriteBySuperEditor,
            permissions.ReadWriteByCurator,
        )
