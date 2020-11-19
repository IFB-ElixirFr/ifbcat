from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.postgres.lookups import Unaccent
from django.db.models.functions import Upper
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html
from django.utils.translation import ugettext

from ifbcat_api import models, business_logic
from ifbcat_api.permissions import simple_override_method


class PermissionInClassModelAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    def has_permission_for_methods(self, *, request, methods: list, obj=None):
        # similar to rest_framework/views.py:APIView.check_permissions#L326
        for perm in business_logic.get_permission_classes(self.model):
            for method in methods:
                with simple_override_method(request=request, method=method) as request:
                    if obj is None:
                        if not perm().has_permission(request=request, view=None):
                            return False
                    else:
                        if not perm().has_object_permission(request=request, view=None, obj=obj):
                            return False
        return True

    def has_view_permission(self, request, obj=None):
        from_super = super().has_view_permission(request=request, obj=obj)
        if not from_super:
            return False
        if obj is None:
            return from_super

        return self.has_permission_for_methods(request=request, obj=obj, methods=["GET"])

    def has_add_permission(self, request):
        from_super = super().has_add_permission(request=request)
        if not from_super:
            return False

        return self.has_permission_for_methods(request=request, methods=["PUT"])

    def has_change_permission(self, request, obj=None):
        from_super = super().has_change_permission(request=request, obj=obj)
        if not from_super:
            return False
        if obj is None:
            return from_super

        return self.has_permission_for_methods(request=request, obj=obj, methods=["POST", "PUT"])

    def has_delete_permission(self, request, obj=None):
        from_super = super().has_delete_permission(request=request, obj=obj)
        if not from_super:
            return False
        if obj is None:
            return from_super
        return self.has_permission_for_methods(request=request, obj=obj, methods=["DELETE"])


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
class UserProfileAdmin(PermissionInClassModelAdmin, UserAdmin):
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
        ('Password', {'fields': ('password',)}),
        ('Personal info', {'fields': ('email', 'firstname', 'lastname', 'orcidid', 'homepage', 'expertise')}),
        (
            'Permissions',
            {
                'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
        (
            'Important dates',
            {'fields': ('last_login',)},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )
    filter_horizontal = ("user_permissions",)
    autocomplete_fields = (
        "expertise",
        "groups",
    )

    def can_manager_user(self, request, obj):
        return business_logic.can_edit_user(request.user, obj)

    def has_change_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or self.can_manager_user(request=request, obj=obj)
            or super().has_change_permission(request=request, obj=obj)
        )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request=request, obj=obj)
        if not request.user.is_superuser:
            readonly_fields += (
                "last_login",
                "is_superuser",
                "user_permissions",
            )
            if not self.can_manager_user(request=request, obj=obj):
                readonly_fields += ("groups",)
            if request.user != obj:
                readonly_fields += ("password",)
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request=request, obj=obj)
        ret = []
        for k, f in fieldsets:
            if request.user.is_superuser or (
                self.can_manager_user(request=request, obj=obj)
                and k != 'Permissions'
                and (request.user == obj or k != "Password")
            ):
                ret.append((k, f))
        return ret


# "search_fields" defines the searchable 'fields'
# "list_filter" adds fields to Django admin filter box
# "filter_horizontal" adds widgets for item selection from lists
@admin.register(models.Event)
class EventAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class TrainingEventAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class KeywordAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ['keyword']


@admin.register(models.EventPrerequisite)
class EventPrerequisiteAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ['prerequisite']


@admin.register(models.Topic)
class TopicAdmin(ViewInApiModelAdmin):
    search_fields = ['topic']


@admin.register(models.EventCost)
class EventCostAdmin(ViewInApiModelAdmin):
    search_fields = ['cost']


admin.site.register(models.EventDate)


@admin.register(models.Trainer)
class TrainerAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'trainerName',
        'trainerEmail',
        'trainerId__name',
    )
    autocomplete_fields = ('trainerId',)


@admin.register(models.TrainingEventMetrics)
class TrainingEventMetricsAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'dateStart',
        'dateEnd',
        'trainingEvent__name',
        'trainingEvent__shortName',
        'trainingEvent__description',
    )
    autocomplete_fields = ('trainingEvent',)


@admin.register(models.EventSponsor)
class EventSponsorAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'name',
        'organisationId__name',
    )
    autocomplete_fields = ('organisationId',)


@admin.register(models.Certification)
class CertificationAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
    )


@admin.register(models.Community)
class CommunityAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
        'homepage',
        'organisations__name',
    )
    autocomplete_fields = ('organisations',)


@admin.register(models.ElixirPlatform)
class ElixirPlatformAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class OrganisationAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class ProjectAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class TrainingMaterialAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class ComputingFacilityAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class TeamAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    ordering = (Upper(Unaccent("name")),)
    search_fields = (
        'name',
        'description',
        'expertise',
        'leader__firstname',
        'leader__lastname',
        'deputies__firstname',
        'deputies__lastname',
        'scientificLeaders__firstname',
        'scientificLeaders__lastname',
        'technicalLeaders__firstname',
        'technicalLeaders__lastname',
        'members__firstname',
        'members__lastname',
        'maintainers__firstname',
        'maintainers__lastname',
    )

    autocomplete_fields = (
        'leader',
        'deputies',
        'scientificLeaders',
        'technicalLeaders',
        'members',
        'maintainers',
    )
    filter_horizontal = (
        'scientificLeaders',
        'technicalLeaders',
        'members',
        'maintainers',
        'deputies',
    )


@admin.register(models.BioinformaticsTeam)
class BioinformaticsTeamAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    ordering = (Unaccent("name"),)
    search_fields = (
        'name',
        'description',
        'expertise',
        'leader__firstname',
        'leader__lastname',
        'deputies__firstname',
        'deputies__lastname',
        'scientificLeaders__firstname',
        'scientificLeaders__lastname',
        'technicalLeaders__firstname',
        'technicalLeaders__lastname',
        'members__firstname',
        'members__lastname',
        'maintainers__firstname',
        'maintainers__lastname',
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
        'certifications__name',
    )

    list_filter = ('fields',)

    autocomplete_fields = (
        'fields',
        'platforms',
        'communities',
        'projects',
    )
    filter_horizontal = (
        'scientificLeaders',
        'technicalLeaders',
        'members',
        'maintainers',
        'deputies',
    )
    list_display = (
        'name',
        'logo',
    )

    def logo(self, obj):
        if obj.logo_url:
            return format_html('<center style="margin: -8px;"><img height="32px" src="' + obj.logo_url + '"/><center>')
        return format_html('<center style="margin: -8px;">-<center>')

    logo.short_description = format_html("<center>" + ugettext("Image") + "<center>")


@admin.register(models.Service)
class ServiceAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class ServiceSubmissionAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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


@admin.register(models.Tool)
class ToolAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ('name',)


class GroupAdminForm(forms.ModelForm):
    """
    https://stackoverflow.com/a/39648244/2144569
    """

    class Meta:
        model = Group
        exclude = []

    # Add the users field.
    users = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        # Use the pretty 'filter_horizontal widget'.
        widget=FilteredSelectMultiple('users', False),
    )

    def __init__(self, *args, **kwargs):
        # Do the normal form initialisation.
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        # If it is an existing group (saved objects have a pk).
        if self.instance.pk:
            # Populate the users field with the current Group users.
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        # Add the users to the Group.
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        # Default save
        instance = super(GroupAdminForm, self).save()
        # Save many-to-many data
        self.save_m2m()
        return instance


# Unregister the original Group admin.
admin.site.unregister(Group)


# Create a new Group admin.
@admin.register(Group)
class GroupAdmin(GroupAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']

    readonly_fields = (
        "name",
        "permissions",
    )

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return super().has_delete_permission(request)
        return obj.name not in [
            business_logic.get_user_manager_group_name(),
        ]


# register all models that are not registered yet
from django.apps import apps

models = apps.get_app_config('ifbcat_api').get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
