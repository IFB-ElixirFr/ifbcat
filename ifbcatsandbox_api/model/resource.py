# Imports
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from ifbcatsandbox_api.model.community import Community
from ifbcatsandbox_api.model.elixirPlatform import ElixirPlatform
from ifbcatsandbox_api.validators import validate_can_be_looked_up


class Resource(models.Model):
    """Resource model: A computing facility, database, tool or training material provided by a bioinformatics team."""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=255, help_text="Name of the resource.", validators=[validate_can_be_looked_up,],)
    description = models.TextField(help_text="A short description of the resource.")
    communities = models.ManyToManyField(
        Community, blank=True, related_name='resources', help_text="Community which uses the resource."
    )
    elixirPlatforms = models.ManyToManyField(
        ElixirPlatform, blank=True, related_name='resources', help_text="ELIXIR Platform which uses the resource."
    )

    def __str__(self):
        """Return the Resource model as a string."""
        return self.name
