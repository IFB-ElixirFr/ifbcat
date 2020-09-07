# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _

from ifbcatsandbox_api.model.community import Community
from ifbcatsandbox_api.model.elixirPlatform import ElixirPlatform
from ifbcatsandbox_api.model.misc import Keyword, Field, Topic, Doi
from ifbcatsandbox_api.model.organisation import Organisation
from ifbcatsandbox_api.model.project import Project
from ifbcatsandbox_api.model.team import Team
from ifbcatsandbox_api.validators import validate_grid_or_ror_id


class BioinformaticsTeam(Team):
    """Bioinformatics team model: A French team whose activities involve the development, deployment, provision, maintenance or support of bioinformatics resources, services or events."""

    # IfbMembershipType: Controlled vocabulary of types of membership bioinformatics teams have to IFB.
    class IfbMembershipType(models.TextChoices):
        """Controlled vocabulary of types of membership bioinformatics  s have to IFB."""

        IFB_PLATFORM = 'IFB platform', _('IFB platform')
        IFB_ASSOCIATED_TEAM = 'IFB-associated team', _('IFB-associated team')
        NOT_A_MEMBER = 'Not a member', _('Not a member')

    # CertificationType: Controlled vocabulary of type of certification of bioinformatics teams.
    class CertificationType(models.TextChoices):
        """Controlled vocabulary of type of certification of bioinformatics teams."""

        CERTIFICATE1 = 'Certificate 1', _('Certificate 1')

    # orgid, ifbMembership & fundedBy are mandatory.
    orgid = models.CharField(
        max_length=255,
        unique=True,
        help_text="Organisation ID (GRID or ROR ID) of the team.",
        validators=[
            validate_grid_or_ror_id,
        ],
        null=True,
        blank=True,
    )
    unitId = models.CharField(
        max_length=255,
        blank=True,
        help_text="Unit ID (unique identifier of research or service unit) that the Bioinformatics Team belongs to.",
    )
    address = models.TextField(blank=True, help_text="Postal address of the bioinformatics team.")
    logo_url = models.URLField(max_length=512, help_text="URL of logo.", blank=True, null=True)
    fields = models.ManyToManyField(
        Field,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="A broad field that the bioinformatics team serves.",
    )
    topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="URIs of EDAM Topic terms describing the bioinformatics team.",
    )
    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="A keyword (beyond EDAM ontology scope) describing the bioinformatics team.",
    )
    ifbMembership = models.CharField(
        max_length=255,
        choices=IfbMembershipType.choices,
        help_text="Type of membership the bioinformatics team has to IFB.",
    )
    affiliatedWith = models.ManyToManyField(
        Organisation,
        blank=True,
        related_name='bioinformaticsTeamsAffiliatedWith',
        help_text="Organisation(s) to which the bioinformatics team is affiliated.",
    )
    platforms = models.ManyToManyField(
        ElixirPlatform,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="ELIXIR Platform(s) in which the bioinformatics team is involved.",
    )
    communities = models.ManyToManyField(
        Community,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="Communities in which the bioinformatics team is involved.",
    )
    projects = models.ManyToManyField(
        Project,
        blank=True,
        related_name='bioinformaticsTeams',
        help_text="Project(s) that the bioinformatics team is involved with, supports or hosts.",
    )
    fundedBy = models.ManyToManyField(
        Organisation,
        related_name='bioinformaticsTeamsFundedBy',
        help_text="Organisation(s) that funds the bioinformatics team.",
    )
    publications = models.ManyToManyField(
        Doi,
        related_name='bioinformaticsTeams',
        blank=True,
        help_text="Publication(s) that describe the team.",
    )
    certification = models.CharField(
        max_length=255,
        blank=True,
        choices=CertificationType.choices,
        help_text="Certification (e.g. ISO) of the bioinformatics team.",
    )
