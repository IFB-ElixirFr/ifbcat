# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _

from ifbcat_api.model.elixirPlatform import ElixirPlatform
from ifbcat_api.model.team import Team
from ifbcat_api.model.misc import Topic


class BioinformaticsTeam(Team):
    """Bioinformatics team model: A French team whose activities involve the development, deployment, provision, maintenance or support of bioinformatics resources, services or events."""

    # IfbMembershipType: Controlled vocabulary of types of membership bioinformatics teams have to IFB.
    class IfbMembershipType(models.TextChoices):
        """Controlled vocabulary of types of membership bioinformatics  s have to IFB."""

        IFB_PLATFORM = 'IFB platform', _('IFB platform')
        IFB_ASSOCIATED_TEAM = 'IFB-associated team', _('IFB-associated team')
        NOT_A_MEMBER = 'Not a member', _('Not a member')

    edamTopics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='bioinformaticsTeamsEdamTopics',
        help_text="URIs of EDAM Topic terms describing the bioinformatics team.",
    )
    ifbMembership = models.CharField(
        max_length=255,
        choices=IfbMembershipType.choices,
        help_text="Type of membership the bioinformatics team has to IFB.",
    )
    platforms = models.ManyToManyField(
        ElixirPlatform,
        blank=True,
        related_name='bioinformaticsTeamsPlatforms',
        help_text="ELIXIR Platform(s) in which the bioinformatics team is involved.",
    )
