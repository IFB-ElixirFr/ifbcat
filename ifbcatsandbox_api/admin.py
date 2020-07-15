from django.contrib import admin
from ifbcatsandbox_api import models

# Models are registered below
# Enable Django admin for user profile and news item models - i.e. make them accessible through admin interface
admin.site.register(models.UserProfile)
admin.site.register(models.NewsItem)
admin.site.register(models.Event)
admin.site.register(models.EventKeyword)
admin.site.register(models.EventPrerequisite)
