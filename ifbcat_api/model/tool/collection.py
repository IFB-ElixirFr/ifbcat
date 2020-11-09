from django.db import models


class Collection(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
