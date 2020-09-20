from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from ifbcat_api import models
from django.urls import reverse, NoReverseMatch
from django.contrib.admin.options import get_content_type_for_model

# A ModelAdmin that try to find for each instance the associated link in the api:
# For a instance pk=42 of class Blabla, we try to get the url 'blabla-detail' with the pk 42. Note that to work the
# prefix used in urls.py must match the class name : router.register('event', ...) is for class Event
class ViewInApiModelAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',)}

    slug_name = "pk"

    def __init__(self, model, admin_site):
        self.list_display += ('view_in_api_in_list',)
        super().__init__(model, admin_site)

    def view_in_api_in_list(self, obj):
        try:
            return format_html(
                '<center><a href="'
                + reverse('%s-detail' % obj.__class__.__name__.lower(), args=[getattr(obj, self.slug_name)])
                + '"><i class="fa fa-external-link"></i></a><center>'
            )
        except NoReverseMatch:
            return format_html('<center><i class="fa fa-ban"></i></center>')

    view_in_api_in_list.short_description = format_html('<center>View in API<center>')


class ViewInApiModelByNameAdmin(ViewInApiModelAdmin):
    slug_name = "name"


# Models are registered below
# Enable Django admin for user profile and news item models - i.e. make them accessible through admin interface


@admin.register(models.UserProfile)
class UserProfileAdmin(UserAdmin):
    # Enables search, filtering and widgets in Django admin interface.
    ordering = ("email",)
    list_display = (
        'email',
        'firstname',
        'lastname',
        'is_active',
        'is_staff',
        'is_superuser',
    )
    search_fields = (
        'firstname',
        'lastname',
        'email',
        'orcidid',
        'expertise__topic',
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('firstname', 'lastname', 'orcidid', 'homepage', 'expertise')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),},),
        ('Important dates', {'fields': ('last_login',)},),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2'),},),)


# admin.site.register(models.UserProfile)


admin.site.register(models.NewsItem)

# "search_fields" defines the searchable 'fields'
# "list_filter" adds fields to Django admin filter box
# "filter_horizontal" adds widgets for item selection from lists
@admin.register(models.Event)
class EventAdmin(ViewInApiModelAdmin):
    """Enables search, filtering and widgets in Django admin interface."""

    search_fields = (
        'name',
        'shortName',
        'description',
        'type',
        'venue',
        'city',
        'country',
        'costs_cost',
        'topics__topic',
        'keywords__keyword',
        'prerequisites__prerequisite',
        'accessibility',
        'accessibilityNote',
        'contactName',
        'contactId__name',
        'contactEmail',
        'market',
        'elixirPlatforms__name',
        'communities__name',
        'hostedBy__name',
        'organisedByTeams__name',
        'organisedByBioinformaticsTeams__name',
        'organisedByOrganisations__name',
        'sponsoredBy__name',
        'sponsoredBy__organisationId__name',
    )
    list_display = ('short_name_or_name', 'contactName')
    list_filter = (
        'type',
        'costs',
        'onlineOnly',
        'accessibility',
        'elixirPlatforms',
        'communities',
        'hostedBy',
    )
    #
    filter_horizontal = ('dates',)
    autocomplete_fields = (
        'costs',
        'topics',
        'keywords',
        'prerequisites',
        'elixirPlatforms',
        'communities',
        'hostedBy',
        'sponsoredBy',
    )

    # date_hierarchy = 'dates'

    def short_name_or_name(self, obj):
        if obj.shortName is None or obj.shortName == "":
            if len(obj.name) <= 35:
                return obj.name
            return "%.32s..." % obj.name
        return obj.shortName

    short_name_or_name.short_description = "Name"


@admin.register(models.TrainingEvent)
class TrainingEventAdmin(ViewInApiModelAdmin):
    """Enables search, filtering and widgets in Django admin interface."""

    search_fields = (
        'audienceTypes__audienceType',
        'audienceRoles__audienceRole',
        'difficultyLevel',
        'learningOutcomes',
    )
    list_filter = (
        'trainingMaterials',
        'computingFacilities',
        # 'databases',
        # 'tools',
    )
    autocomplete_fields = (
        'trainingMaterials',
        'computingFacilities',
    )


@admin.register(models.Keyword)
class KeywordAdmin(ViewInApiModelAdmin):
    search_fields = ['keyword']


@admin.register(models.EventPrerequisite)
class EventPrerequisiteAdmin(ViewInApiModelAdmin):
    search_fields = ['prerequisite']


@admin.register(models.Topic)
class TopicAdmin(ViewInApiModelAdmin):
    search_fields = ['topic']


@admin.register(models.EventCost)
class EventCostAdmin(ViewInApiModelAdmin):
    search_fields = ['cost']


admin.site.register(models.EventDate)


@admin.register(models.Trainer)
class TrainerAdmin(ViewInApiModelAdmin):
    search_fields = (
        'trainerName',
        'trainerEmail',
        'trainerId__name',
    )
    autocomplete_fields = ('trainerId',)


@admin.register(models.TrainingEventMetrics)
class TrainingEventMetricsAdmin(ViewInApiModelAdmin):
    search_fields = (
        'dateStart',
        'dateEnd',
        'trainingEvent__name',
        'trainingEvent__shortName',
        'trainingEvent__description',
    )
    autocomplete_fields = ('trainingEvent',)


@admin.register(models.EventSponsor)
class EventSponsorAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'organisationId__name',
    )
    autocomplete_fields = ('organisationId',)


@admin.register(models.Community)
class CommunityAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
        'homepage',
        'organisations__name',
    )
    autocomplete_fields = ('organisations',)


@admin.register(models.ElixirPlatform)
class ElixirPlatformAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
        'homepage',
        'coordinator__firstname',
        'coordinator__lastname',
        'coordinator__email',
        'deputies__firstname',
        'deputies__lastname',
        'deputies__email',
    )


@admin.register(models.Organisation)
class OrganisationAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
        'homepage',
        'orgid',
        'fields__field',
        'city',
    )
    list_filter = ('fields',)
    autocomplete_fields = ('fields',)


@admin.register(models.Field)
class FieldAdmin(ViewInApiModelAdmin):
    search_fields = ('field',)


@admin.register(models.Project)
class ProjectAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'homepage',
        'description',
        'topics__topic',
        'team__name',
        'hostedBy__name',
        'fundedBy__name',
        'communities__name',
        'elixirPlatforms__name',
        'uses_name',
    )
    list_filter = ('elixirPlatforms', 'communities', 'hostedBy', 'uses')
    autocomplete_fields = (
        'topics',
        'elixirPlatforms',
        'communities',
        'team',
        'hostedBy',
        'fundedBy',
        'uses',
    )


@admin.register(models.AudienceRole)
class AudienceRoleAdmin(ViewInApiModelAdmin):
    search_fields = ['audienceRole']


@admin.register(models.AudienceType)
class AudienceTypeAdmin(ViewInApiModelAdmin):
    search_fields = ['audienceType']


@admin.register(models.TrainingMaterial)
class TrainingMaterialAdmin(ViewInApiModelAdmin):
    search_fields = (
        'doi__doi',
        'fileName',
        'topics__topic',
        'keywords__keyword',
        'audienceTypes__audienceType',
        'audienceRoles__audienceRole',
        'difficultyLevel',
        'providedBy__name',
        'license',
    )

    autocomplete_fields = (
        'communities',
        'elixirPlatforms',
        'topics',
        'keywords',
        'audienceTypes',
        'audienceRoles',
    )


@admin.register(models.ComputingFacility)
class ComputingFacilityAdmin(ViewInApiModelAdmin):
    search_fields = (
        'homepage',
        'providedBy__name',
        'team__name',
        'accessibility',
        'serverDescription',
    )

    list_filter = ('accessibility',)

    autocomplete_fields = (
        'providedBy',
        'team',
        'trainingMaterials',
    )


@admin.register(models.Team)
class TeamAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
        'expertise',
        'leader__firstname',
        'leader__lastname',
        'deputies__firstname',
        'deputies__lastname',
        'scientificLeader__firstname',
        'scientificLeader__lastname',
        'technicalLeader__firstname',
        'technicalLeader__lastname',
        'members__firstname',
        'members__lastname',
        'maintainers__firstname',
        'maintainers__lastname',
    )

    autocomplete_fields = (
        'leader',
        'deputies',
        'scientificLeader',
        'technicalLeader',
        'members',
        'maintainers',
    )


@admin.register(models.BioinformaticsTeam)
class BioinformaticsTeamAdmin(ViewInApiModelAdmin):
    search_fields = (
        'orgid',
        'unitId',
        'address',
        'fields',
        'topics__topic',
        'keywords__keyword',
        'ifbMembership',
        'platforms__name',
        'communities__name',
        'projects__name',
        'fundedBy__name',
        'publications__doi',
        'certification',
    )

    list_filter = ('fields',)

    autocomplete_fields = (
        'fields',
        'platforms',
        'communities',
        'projects',
    )


@admin.register(models.Service)
class ServiceAdmin(ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
        'bioinformaticsTeams__name',
        'computingFacilities__name',
        'trainingEvents__name',
        'trainingMaterials__name',
        'publications__doi',
    )

    autocomplete_fields = (
        'bioinformaticsTeams',
        'computingFacilities',
        'trainingEvents',
        'trainingMaterials',
    )


@admin.register(models.ServiceSubmission)
class ServiceSubmissionAdmin(ViewInApiModelAdmin):
    search_fields = (
        'service__name',
        'authors_firstname',
        'authors_lastname',
        'submitters_firstname',
        'submitters_lastname',
        'year',
        'motivation',
        'scope',
        'caseForSupport',
        'qaqc',
        'usage',
        'sustainability',
    )

    autocomplete_fields = ('service',)


# register all models that are not registered yet
from django.apps import apps

models = apps.get_app_config('ifbcat_api').get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
