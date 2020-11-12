# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _


class Certification(models.Model):
    """Community model: A group of people collaborating on a common scientific or technical topic, including formal ELIXIR  Communities, emerging ELIXIR communities, ELXIR focus groups, IFB communities, and others."""

    # name, description & homepage are mandatory
    name = models.CharField(max_length=255, unique=True, help_text="Name of the certification, e.g. 'Label IBiSA'.")

    description = models.TextField(help_text="Short description of the certification.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the certification.")

    class Meta:
        # To overide simply an 's' being appended to "Community" (== "Communitys") in Django admin interface
        verbose_name_plural = "Certifications"

    def __str__(self):
        """Return the Certification model as a string."""
        return self.name
