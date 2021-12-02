# Imports
from django.db import models

from ifbcat_api.model.community import Community
from ifbcat_api.model.elixirPlatform import ElixirPlatform
from ifbcat_api.validators import validate_can_be_looked_up


class Resource(models.Model):
    """Resource model: A computing facility, database, tool or training material provided by a bioinformatics team."""

    class Meta:
        abstract = True

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the resource.",
        validators=[
            validate_can_be_looked_up,
        ],
    )
    description = models.TextField(help_text="A short description of the resource.")
    communities = models.ManyToManyField(Community, blank=True, help_text="Community which uses the resource.")
    elixirPlatforms = models.ManyToManyField(
        ElixirPlatform, blank=True, help_text="ELIXIR Platform which uses the resource."
    )

    def __str__(self):
        """Return the Resource model as a string."""
        return self.name
