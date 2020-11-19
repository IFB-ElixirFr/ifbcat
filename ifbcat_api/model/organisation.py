# Imports
from django.conf import settings
from django.db import models
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.misc import Field
from ifbcat_api.validators import validate_grid_or_ror_id, validate_can_be_looked_up


class Organisation(models.Model):
    """A legal entity involved in research and development, or its support, primarily but not exclusively French organisations directly or indirectly related to bioinformatics."""

    # name, description & homepage are mandatory
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the organisation.",
        validators=[
            validate_can_be_looked_up,
        ],
    )
    description = models.TextField(help_text="Short description of the organisation.")
    homepage = models.URLField(max_length=255, help_text="Homepage of the organisation.")

    # orgid is not mandatory, but if specified must be unique, so we cannot have blank=True.
    # Two NULL values do not equate to being the same, whereas two blank values would!
    orgid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text="Organisation ID (GRID or ROR ID) of the organisation.",
        validators=[
            validate_grid_or_ror_id,
        ],
    )
    fields = models.ManyToManyField(
        Field,
        blank=True,
        related_name='organisations',
        help_text="A broad field that the organisation serves.",
    )
    city = models.CharField(max_length=255, blank=True, help_text="Nearest city to the organisation.")
    logo_url = models.URLField(max_length=512, help_text="URL of logo of organisation.", blank=True, null=True)

    def __str__(self):
        """Return the Organisation model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (permissions.PubliclyReadableEditableByOwner, IsAuthenticatedOrReadOnly)
