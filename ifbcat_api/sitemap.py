from django.contrib import sitemaps
from django.urls import reverse

from ifbcat_api import models


class TeamSitemap(sitemaps.Sitemap):
    changefreq = "monthly"

    def __init__(self, location_prefix=''):
        self.location_prefix = location_prefix
        super().__init__()

    def items(self):
        return models.Team.annotate_is_active().filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, item):
        return reverse(f'{self.location_prefix}{item.__class__.__name__.lower()}-detail', args=[item.name])


class AbstractEventSitemap(sitemaps.Sitemap):
    changefreq = "weekly"

    def __init__(self, klass, location_prefix=''):
        self.location_prefix = location_prefix
        self.klass = klass
        super().__init__()

    def items(self):
        return self.klass.objects.filter(is_draft=False)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, item):
        return reverse(f'{self.location_prefix}{self.klass.__name__.lower()}-detail', args=[item.pk])


my_sitemaps = {
    'team': TeamSitemap(),
    'team-vfront': TeamSitemap(location_prefix='vfront:'),
    'event': AbstractEventSitemap(klass=models.Event),
    'event-vfront': AbstractEventSitemap(klass=models.Event, location_prefix='vfront:'),
    'training': AbstractEventSitemap(klass=models.Training),
    'training-vfront': AbstractEventSitemap(klass=models.Training, location_prefix='vfront:'),
}