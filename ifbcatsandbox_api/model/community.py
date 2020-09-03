# Imports
from django.db import models
from django.utils.translation import gettext_lazy as _

from ifbcatsandbox_api.model.organisation import Organisation


class Community(models.Model):
    """Community model: A group of people collaborating on a common scientific or technical topic, including formal ELIXIR  Communities, emerging ELIXIR communities, ELXIR focus groups, IFB communities, and others."""

    # EventType: Controlled vocabulary of types of events.
    class CommunityName(models.TextChoices):
        """Controlled vocabulary of names of communities."""

        # NB: Note "BIOINFO not 3D-BIOINFO" because of Python variable name restrictions.
        BIOINFO = '3D-BioInfo', _('3D-BioInfo')
        GALAXY = 'Galaxy', _('Galaxy')
        INTRINSICALLY_DISORDERED_PROTEINS = 'Intrinsically Disordered Proteins', _('Intrinsically Disordered Proteins')
        MARINE_METAGENOMICS = 'Marine Metagenomics', _('Marine Metagenomics')
        METABOLOMICS = 'Metabolomics', _('Metabolomics')
        MICROBIAL_BIOTECHNOLOGY = 'Microbial Biotechnology', _('Microbial Biotechnology')
        PLANT_SCIENCES = 'Plant Sciences', _('Plant Sciences')
        PROTEOMICS = 'Proteomics', _('Proteomics')
        FEDERATED_HUMAN_DATA = 'Federated Human Data', _('Federated Human Data')
        HUMAN_COPY_NUMBER_VARIATION = 'Human Copy Number Variation', _('Human Copy Number Variation')
        RARE_DISEASES = 'Rare Diseases', _('Rare Diseases')

    # name, description & homepage are mandatory
    name = models.CharField(
        max_length=255, choices=CommunityName.choices, unique=True, help_text="Name of the community, e.g. 'Galaxy'."
    )

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
