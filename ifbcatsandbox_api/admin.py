from django.contrib import admin
from ifbcatsandbox_api import models

# Models are registered below
# Enable Django admin for user profile model - i.e. make it accessible through admin interface
admin.site.register(models.UserProfile)
