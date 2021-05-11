from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ifbcat_api import permissions
from ifbcat_api.model.event import Event


class TrainingCourseMetrics(models.Model):
    """Training event metrics model: Metrics and other information for a specific training event."""

    # dateStart and dateEnd are mandatory
    dateStart = models.DateField(help_text="The start date of the training event.")
    dateEnd = models.DateField(help_text="The end date of the training event.")
    numParticipants = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of participants at the training event.",
        validators=[
            MinValueValidator(1),
        ],
    )

    event = models.ForeignKey(
        Event,
        related_name='metrics',
        on_delete=models.CASCADE,
        help_text="Training event to which the metrics are associated.",
    )

    class Meta:
        verbose_name_plural = "Training event metrics"

    def __str__(self):
        return self.dateStart.__str__()

    @classmethod
    def get_permission_classes(cls):
        # TODO let trainer and/or bio team edit it ?
        return (
            permissions.ReadOnly | permissions.ReadWriteBySuperEditor,
            IsAuthenticatedOrReadOnly,
        )
