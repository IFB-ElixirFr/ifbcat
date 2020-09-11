# Imports
from django.conf import settings
from django.db import models

from ifbcat_api.model.community import Community
from ifbcat_api.model.computingFacility import ComputingFacility
from ifbcat_api.model.elixirPlatform import ElixirPlatform
from ifbcat_api.model.misc import Topic
from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team
from ifbcat_api.validators import validate_can_be_looked_up


class Project(models.Model):
    """Project model: A scientific or technical project that a French bioinformatics team is involved in."""

    # name, homepage & description are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(
        max_length=255,
        help_text="Name of the project.",
        unique=True,
        validators=[
            validate_can_be_looked_up,
        ],
    )
    homepage = models.URLField(max_length=255, help_text="Homepage of the project.")
    description = models.TextField(help_text="Description of the project.")
    topics = models.ManyToManyField(
        Topic,
        related_name='projects',
        blank=True,
        help_text="URIs of EDAM Topic terms describing the expertise of the project.",
    )
    team = models.ForeignKey(
        Team,
        related_name='project',
        null=True,
        on_delete=models.SET_NULL,
        help_text="The team which is delivering the project.",
    )
    hostedBy = models.ManyToManyField(
        Organisation,
        blank=True,
        related_name='projectsHosts',
        help_text="Organisation that hosts the project.",
    )
    fundedBy = models.ManyToManyField(
        Organisation,
        blank=True,
        related_name='projectsFunders',
        help_text="Organisation that funds the project.",
    )
    communities = models.ManyToManyField(
        Community,
        blank=True,
        related_name='projects',
        help_text="Community for which the project is relevant.",
    )
    elixirPlatforms = models.ManyToManyField(
        ElixirPlatform,
        blank=True,
        related_name='projects',
        help_text="ELIXIR Platform to which the project is relevant.",
    )
    uses = models.ManyToManyField(
        ComputingFacility,
        blank=True,
        related_name='projects',
        help_text="A computing facility which the project uses.",
    )

    def __str__(self):
        """Return the Project model as a string."""
        return self.name
