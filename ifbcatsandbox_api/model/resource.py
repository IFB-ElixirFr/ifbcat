# Imports
from django.db import models
from django.core import validators

from ifbcatsandbox_api.model.userProfile import *
from ifbcatsandbox_api.model.elixirPlatform import *
from ifbcatsandbox_api.model.community import *

# Resource model
class Resource(models.Model):
    """Resource model: A computing facility, database, tool or training material provided by a bioinformatics team."""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    name = models.CharField(
        max_length=255,
        help_text="Name of the resource.",
        validators=[
            validators.RegexValidator(r'^[a-zA-Z0-9 \-_~]+$', 'Should only contains char such as ^[a-zA-Z0-9\-_~]'),
        ],
    )
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
