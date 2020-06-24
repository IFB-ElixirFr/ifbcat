from django.contrib import admin

# Register your models here.
from profiles_api import models

admin.site.register(models.UserProfile)
admin.site.register(models.ProfileFeedItem)
