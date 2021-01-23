from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.service import Service
from ifbcat_api.model.userProfile import UserProfile


class ServiceSubmission(models.Model):
    """Service submission model: Metadata for a service that is included as part of the submission of the service to a ELIXIR-FR SDP submission process."""

    # All fields are mandatory !
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    service = models.ForeignKey(
        Service,
        related_name='ServiceSubmission',
        null=True,
        on_delete=models.SET_NULL,
        help_text="The service associated with this submission to the ELIXIR FR SDP process.",
    )
    authors = models.ManyToManyField(
        UserProfile,
        related_name='ServiceSubmissionAuthor',
        help_text="The person(s) who submitted the service proposal to the ELIXIR FR SDP process.",
    )
    submitters = models.ManyToManyField(
        UserProfile,
        related_name='ServiceSubmissionSubmitter',
        help_text="The person(s) who submitted the service proposal to the ELIXIR FR SDP process.",
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        help_text="The year when the service was submitted for consideration of inclusion in the French SDP.",
        validators=[
            MinValueValidator(2020),
            MaxValueValidator(2050),
        ],
    )
    motivation = models.TextField(help_text="Motivation for making the submission.")
    scope = models.TextField(
        help_text="Scope of the service including domain covered, relevance, originality, links with EU infrastructures, community leadership roles, and positioning regarding similar resources (especially of ELIXIR nodes and platforms)."
    )
    caseForSupport = models.TextField(
        help_text="The motivation for the service and why it should be supported by IFB and/or included in the SDP."
    )
    qaqc = models.TextField(
        help_text="Short description of quality assurance and control processes in place aimed to ensure a high-quality service."
    )
    usage = models.TextField(
        help_text="Description of the extent and ways the service is used, including quantitatve usage metrics or indicators."
    )
    sustainability = models.TextField(
        help_text="Service funding and sustainability plan, including past and future funding commitments, and number of FTE engaged during the last four years and next year."
    )

    @classmethod
    def get_permission_classes(cls):
        return (
            permissions.ReadOnly
            | permissions.ReadWriteByOwner
            | permissions.ReadWriteBySubmitters
            | permissions.ReadWriteByAuthors
            | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )
