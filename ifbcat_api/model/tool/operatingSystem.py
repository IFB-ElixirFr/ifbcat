from django.db import models

from ifbcat_api import permissions


class OperatingSystem(models.Model):
    OPERATING_SYSTEM_CHOICES = (('LINUX', 'Linux'), ('WINDOWS', 'Windows'), ('MAC', 'Mac'))

    name = models.CharField(unique=True, max_length=100, blank=True, null=True, choices=OPERATING_SYSTEM_CHOICES)

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_permission_classes(cls):
        return (permissions.ReadOnly | permissions.ReadWriteBySuperuser,)


# class OperatingSystem(models.Model):
# 	name = models.CharField(max_length=100, blank=True, null=True)
# 	tool_id = models.ForeignKey(Tool, null=True, blank=True, related_name='operatingSystem', on_delete=models.CASCADE)
#
# 	# metadata
# 	additionDate = models.DateTimeField(auto_now_add=True)
#
# 	def __unicode__(self):
# 		return unicode(self.name) or u''
