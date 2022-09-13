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
    def __init__(self, klass, location_prefix='', for_tess=False):
        self.location_prefix = location_prefix
        self.klass = klass
        self.for_tess = for_tess
        super().__init__()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, item):
        location = reverse(f'{self.location_prefix}{self.klass.__name__.lower()}-detail', args=[item.pk])
        if self.for_tess:
            return f'{location}?format=json-ld'
        return location


class EventSitemap(AbstractEventSitemap):
    def __init__(self, *args, **kwargs):
        super().__init__(klass=models.Event, *args, **kwargs)

    def items(self):
        qs = self.klass.annotate_registration_realisation_status()
        if self.for_tess:
            qs = self.klass.annotate_is_tess_publishing(qs)
            qs = qs.filter(is_tess_publishing=True)
        return qs.filter(is_draft=False)

    def changefreq(self, obj):
        if obj.realisation_status == 'past':
            return 'yearly'
        if obj.registration_status == 'open' or obj.registration_status == 'future':
            return 'daily'
        return 'weekly'


class TrainingSitemap(AbstractEventSitemap):
    changefreq = "weekly"

    def __init__(self, *args, **kwargs):
        super().__init__(klass=models.Training, *args, **kwargs)

    def items(self):
        qs = models.Training.objects.all()
        if self.for_tess:
            qs = qs.filter(tess_publishing=True)
        return qs.filter(is_draft=False)


class TrainingMaterialsSitemap(sitemaps.Sitemap):
    changefreq = "monthly"

    def __init__(self, location_prefix='', for_tess=False):
        self.location_prefix = location_prefix
        self.for_tess = for_tess
        super().__init__()

    def items(self):
        return models.TrainingMaterial.objects.all()

    def location(self, item):
        location = reverse(f'{self.location_prefix}{item.__class__.__name__.lower()}-detail', args=[item.name])
        if self.for_tess:
            return f'{location}?format=json-ld'
        return location


general = {
    'team': TeamSitemap(),
    'team-vfront': TeamSitemap(location_prefix='vfront:'),
    'event': EventSitemap(),
    'event-vfront': EventSitemap(location_prefix='vfront:'),
    'training': TrainingSitemap(),
    'training-vfront': TrainingSitemap(location_prefix='vfront:'),
    'training-materials': TrainingMaterialsSitemap(),
    # 'training-materials-vfront': TrainingSitemap(Material, location_prefix='vfront:'),
}

tess = {
    'event': EventSitemap(for_tess=True),
    'training': TrainingSitemap(for_tess=True),
    'training-materials': TrainingMaterialsSitemap(for_tess=True),
}
