# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator

from ifbcatsandbox_api.model.userProfile import *
from ifbcatsandbox_api.model.misc import *


# Team model
class Team(models.Model):
    """Team model: A group of people collaborating on a common project or goals, or organised (formally or informally) into some structure."""

    # name, description, homepage, members & maintainers are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the team.",
        validators=[RegexValidator(r'^[a-zA-Z0-9 \-_~]+$', 'Should only contains char such as ^[a-zA-Z0-9\-_~]'),],
    )
    description = models.TextField(help_text="Description of the team.")
    homepage = models.URLField(max_length=255, null=True, blank=True, help_text="Homepage of the team.")
    expertise = models.ManyToManyField(
        Topic, related_name='teams', help_text="URIs of EDAM Topic terms describing the expertise of the team.",
    )
    leader = models.ForeignKey(
        UserProfile, related_name='teamLeader', null=True, on_delete=models.SET_NULL, help_text="Leader of the team.",
    )
    deputies = models.ManyToManyField(
        UserProfile, related_name='teamDeputies', blank=True, help_text="Deputy leader(s) of the team.",
    )
    scientificLeader = models.ForeignKey(
        UserProfile,
        related_name='teamScientificLeader',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Scientific leader of the team.",
    )
    technicalLeader = models.ForeignKey(
        UserProfile,
        related_name='teamTechnicalLeader',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Technical leader of the team.",
    )
    members = models.ManyToManyField(UserProfile, related_name='teamMembers', help_text="Members of the team.",)
    maintainers = models.ManyToManyField(
        UserProfile, related_name='teamMaintainers', help_text="Maintainer(s) of the team metadata in IFB catalogue.",
    )

    def __str__(self):
        """Return the Team model as a string."""
        return self.name
