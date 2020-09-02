# Imports
from django.db import models
from django.core.validators import RegexValidator

from ifbcatsandbox_api.model.userProfile import *
from ifbcatsandbox_api.model.misc import *


# Organisation model
class Organisation(models.Model):
    """A legal entity involved in research and development, or its support, primarily but not exclusively French organisations directly or indirectly related to bioinformatics."""

    # name, description & homepage are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the organisation.",
        validators=[RegexValidator(r'^[a-zA-Z0-9 \-_~]+$', 'Should only contains char such as ^[a-zA-Z0-9\-_~]'),],
    )
    description = models.TextField(help_text="Short description of the organisation.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the organisation.")

    # orgid is not mandatory, but if specified must be unique, so we cannot have blank=True.
    # Two NULL values do not equate to being the same, whereas two blank values would!
    orgid = models.CharField(
        max_length=255, null=True, unique=True, help_text="Organisation ID (GRID or ROR ID) of the organisation.",
    )
    fields = models.ManyToManyField(
        Field, blank=True, related_name='organisations', help_text="A broad field that the organisation serves.",
    )
    city = models.CharField(max_length=255, blank=True, help_text="Nearest city to the organisation.")
    # logo ... TO_DO

    def __str__(self):
        """Return the Organisation model as a string."""
        return self.name
