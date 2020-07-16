from django.contrib import admin
from django.utils.html import format_html

from ifbcatsandbox_api import models
from django.urls import reverse, NoReverseMatch
from django.contrib.admin.options import get_content_type_for_model

# A ModelAdmin that try to find for each instance the associated link in the api:
# For a instance pk=42 of class Blabla, we try to get the url 'blabla-detail' with the pk 42. Note that to work the
# prefix used in urls.py must match the class name : router.register('event', ...) is for class Event
class ViewInApiModelAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',)
        }

    def __init__(self, model, admin_site):
        self.list_display += ('view_in_api_in_list',)
        super().__init__(model, admin_site)

    def view_in_api_in_list(self, obj):
        try:
            return format_html(
                '<center><a href="' + reverse('%s-detail' % obj.__class__.__name__.lower(), args=[obj.pk])
                + '"><i class="fa fa-external-link"></i></a><center>')
        except NoReverseMatch:
            return format_html('<center><i class="fa fa-ban"></i></center>')

    view_in_api_in_list.short_description = format_html('<center>View in API<center>')


# Models are registered below
# Enable Django admin for user profile and news item models - i.e. make them accessible through admin interface
admin.site.register(models.UserProfile)
admin.site.register(models.NewsItem)


@admin.register(models.Event)
class EventAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'shortName',
        'description',
        'homepage',
        'venue',
        'city',
        'country',
        'topics__topic',
        'keywords__keyword',
        'prerequisites__prerequisite',
        'contactName',
        'market',
    )
    list_display = (
        'short_name_or_name',
        'contactName'
    )
    list_filter = (
        'type',
        'cost',
        'onlineOnly',
        'accessibility',
    )
    filter_horizontal = (
        'topics',
        'keywords',
        'prerequisites',
    )

    # date_hierarchy = 'dates'

    def short_name_or_name(self, obj):
        if obj.shortName is None or obj.shortName == "":
            if len(obj.name) <= 35:
                return obj.name
            return "%.32s..." % obj.name
        return obj.shortName

    short_name_or_name.short_description = "Name"


admin.site.register(models.EventKeyword)
admin.site.register(models.EventPrerequisite)
admin.site.register(models.EventTopic)
