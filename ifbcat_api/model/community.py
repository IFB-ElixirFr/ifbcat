# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.organisation import Organisation


class Community(models.Model):
    """Community model: A group of people collaborating on a common scientific or technical topic, including formal ELIXIR  Communities, emerging ELIXIR communities, ELXIR focus groups, IFB communities, and others."""

    # name, description & homepage are mandatory
    name = models.CharField(max_length=255, unique=True, help_text="Name of the community, e.g. 'Galaxy'.")

    description = models.TextField(help_text="Short description of the community.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the community.")
    organisations = models.ManyToManyField(
        Organisation,
        blank=True,
        related_name='communities',
        help_text="An organisation to which the community is affiliated.",
    )

    class Meta:
        # To overide simply an 's' being appended to "Community" (== "Communitys") in Django admin interface
        verbose_name_plural = "Communities"

    def __str__(self):
        """Return the Community model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly | permissions.ReadWriteByCurator | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )
