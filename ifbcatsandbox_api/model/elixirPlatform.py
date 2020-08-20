# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _

from ifbcatsandbox_api.model.userProfile import *


# ELIXIR Platform model
class ElixirPlatform(models.Model):
    """ELIXIR Platform model: An official ELIXIR Platform, bringing together experts to define the strategy and provide services in a particular area."""

    # EventType: Controlled vocabulary of types of events.
    class ElixirPlatformName(models.TextChoices):
        """Controlled vocabulary of names of ELIXIR Platforms."""

        DATA = 'Data', _('Data')
        TOOLS = 'Tools', _('Tools')
        COMPUTE = 'Compute', _('Compute')
        INTEROPERABILITY = 'Interoperability', _('Interoperability')
        TRAINING = 'Training', _('Training')

    # name, description, homepage & coordinator are mandatory
    # null=True is set for coordinator, in case the UserProfile of the coordinator is deleted.
    name = models.CharField(
        max_length=255,
        choices=ElixirPlatformName.choices,
        unique=True,
        help_text="Name of the ELIXIR Platform, e.g. 'Tools'.",
    )

    description = models.TextField(help_text="Short description of the ELIXIR Platform.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the ELIXR Platform.")
    coordinator = models.ForeignKey(
        UserProfile,
        related_name='elixirPlatformCoordinator',
        null=True,
        on_delete=models.SET_NULL,
        help_text="Coordinator of the ELIXIR Platform activities in France.",
    )
    deputies = models.ManyToManyField(
        UserProfile,
        related_name='elixirPlatformDeputies',
        blank=True,
        help_text="Deputy coordinator of the ELIXIR Platform activities in France.",
    )

    def __str__(self):
        """Return the ElixirPlatform model as a string."""
        return self.name
