from django.db import models

from ifbcat_api import permissions


class TypeRole(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the TypeRole model as a string."""
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (permissions.PubliclyReadableByUsersEditableBySuperuser,)


class ToolCredit(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)
    orcidid = models.CharField(max_length=100, blank=True, null=True)
    gridid = models.CharField(max_length=100, blank=True, null=True)
    typeEntity = models.CharField(max_length=100, blank=True, null=True)
    # typeRole = models.CharField(max_length=100, blank=True, null=True)
    note = models.CharField(max_length=2000, blank=True, null=True)

    # many to many
    type_role = models.ManyToManyField(TypeRole, blank=True)

    def __str__(self):
        return str(self.name)

    def __str__(self):
        """Return the Doi model as a string."""
        return self.doi

    @classmethod
    def get_permission_classes(cls):
        return (permissions.PubliclyReadableByUsersEditableBySuperuser,)
