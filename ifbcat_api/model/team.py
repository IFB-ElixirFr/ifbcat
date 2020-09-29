# Imports
from django.conf import settings
from django.db import models

from ifbcat_api.model.misc import Topic
from ifbcat_api.model.userProfile import UserProfile
from ifbcat_api.validators import validate_can_be_looked_up


class Team(models.Model):
    """Team model: A group of people collaborating on a common project or goals, or organised (formally or informally) into some structure."""

    # name, description, homepage, members & maintainers are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
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
    expertise = models.ManyToManyField(
        Topic,
        related_name='teams',
        blank=True,
        help_text="URIs of EDAM Topic terms describing the expertise of the team.",
    )
    leader = models.ForeignKey(
        UserProfile,
        related_name='teamLeader',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Leader of the team.",
    )
    deputies = models.ManyToManyField(
        UserProfile,
        related_name='teamDeputies',
        help_text="Deputy leader(s) of the team.",
    )
    scientificLeader = models.ManyToManyField(
        UserProfile,
        related_name='teamScientificLeaders',
        help_text="Scientific leader(s) of the team.",
    )
    technicalLeader = models.ManyToManyField(
        UserProfile,
        related_name='teamTechnicalLeaders',
        help_text="Technical leader(s) of the team.",
    )
    members = models.ManyToManyField(
        UserProfile,
        related_name='teamMembers',
        help_text="Members of the team.",
    )
    maintainers = models.ManyToManyField(
        UserProfile,
        related_name='teamMaintainers',
        help_text="Maintainer(s) of the team metadata in IFB catalogue.",
    )

    def __str__(self):
        """Return the Team model as a string."""
        return self.name
