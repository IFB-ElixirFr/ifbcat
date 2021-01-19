# Imports
from django.db import models
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions


class Certification(models.Model):
    """Community model: A group of people collaborating on a common scientific or technical topic, including formal ELIXIR  Communities, emerging ELIXIR communities, ELXIR focus groups, IFB communities, and others."""

    # name, description & homepage are mandatory
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the certification, e.g. 'Label IBiSA'.",
        # Validator to avoid if we want to keeep "CATI / CTAI" certifcation
        # validators=[
        #    validate_can_be_looked_up,
        # ],
    )

    description = models.TextField(help_text="Short description of the certification.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the certification.")

    class Meta:
        # To overide simply an 's' being appended to "Community" (== "Communitys") in Django admin interface
        verbose_name_plural = "Certifications"

    def __str__(self):
        """Return the Certification model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly | permissions.UserCanAddNew | permissions.SuperuserCanDelete,
            IsAuthenticatedOrReadOnly,
        )
