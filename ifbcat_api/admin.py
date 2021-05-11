import itertools

import requests
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.postgres.lookups import Unaccent
from django.db.models import Count, Q, When, Value, BooleanField, Case, Min, Max, CharField, F
from django.db.models.functions import Upper, Length
from django.urls import reverse, NoReverseMatch
from django.utils import dateformat
from django.utils.html import format_html
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from rest_framework.authtoken.models import Token

from ifbcat_api import models, business_logic
from ifbcat_api.misc import BibliographicalEntryNotFound
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


class ViewInApiModelAdmin(admin.ModelAdmin, DynamicArrayMixin):
    class Media:
        js = ("js/django_better_admin_arrayfield.min.js",)
        css = {
            "all": (
                "css/django_better_admin_arrayfield.min.css",
                # "css/ifbcat_admin.css",
                # 'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
            )
        }

    slug_name = "pk"

    def __init__(self, model, admin_site):
        self.list_display += ('view_in_api_in_list',)
        super().__init__(model, admin_site)

    def view_in_api_in_list(self, obj):
        try:
            return format_html(
                '<center><a href="'
                + reverse('%s-detail' % obj.__class__.__name__.lower(), args=[getattr(obj, self.slug_name)])
                + '"><i class="fa fa-external-link-alt"></i></a><center>'
            )
        except NoReverseMatch:
            return format_html('<center><i class="fa fa-ban"></i></center>')

    view_in_api_in_list.short_description = format_html('<center>View in API<center>')


class ViewInApiModelByNameAdmin(ViewInApiModelAdmin):
    slug_name = "name"


# Models are registered below
# Enable Django admin for user profile and news item models - i.e. make them accessible through admin interface


@admin.register(models.UserProfile)
class UserProfileAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin, UserAdmin):
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
        'expertise__uri',
    )
    fieldsets = (
        ('Personal info', {'fields': ('email', 'firstname', 'lastname', 'orcidid', 'homepage', 'expertise')}),
        ('Password', {'fields': ('password',)}),
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
    filter_horizontal = (
        "user_permissions",
        "groups",
    )
    autocomplete_fields = ("expertise",)

    def can_manager_user(self, request, obj):
        return business_logic.can_edit_user(request.user, obj)

    def has_change_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or self.can_manager_user(request=request, obj=obj)
            or super().has_change_permission(request=request, obj=obj)
        )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = set(super().get_readonly_fields(request=request, obj=obj))
        if not request.user.is_superuser:
            readonly_fields |= set(itertools.chain(*[d['fields'] for _, d in self.fieldsets]))
            if request.user == obj:
                readonly_fields.discard("email")
                readonly_fields.discard("password")
                readonly_fields.discard("firstname")
                readonly_fields.discard("lastname")
                readonly_fields.discard("homepage")
                readonly_fields.discard("orcidid")
                readonly_fields.discard("expertise")
            if self.can_manager_user(request=request, obj=obj):
                readonly_fields.discard("firstname")
                readonly_fields.discard("lastname")
                readonly_fields.discard("homepage")
                readonly_fields.discard("orcidid")
                readonly_fields.discard("expertise")
                if obj is not None and not obj.is_superuser:
                    readonly_fields.discard("groups")
                    readonly_fields.discard("is_active")
                    readonly_fields.discard("is_staff")
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request=request, obj=obj)
        ret = []
        for k, f in fieldsets:
            if request.user.is_superuser or (
                (self.can_manager_user(request=request, obj=obj) or request.user == obj)
                and k != 'Permissions'
                and (request.user == obj or k != "Password")
            ):
                ret.append((k, f))
        return ret

    def get_queryset(self, request):
        if request.user.is_superuser or business_logic.is_user_manager(user=request.user):
            return super().get_queryset(request)
        return super().get_queryset(request).filter(pk=request.user.pk)


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
        'topics__uri',
        'keywords__keyword',
        'prerequisites__prerequisite',
        'accessibilityNote',
        'contactName',
        'contactId__email',
        'contactEmail',
        'organisedByTeams__name',
        'organisedByOrganisations__name',
        'sponsoredBy__name',
        'sponsoredBy__organisationId__name',
    )
    list_display = ('short_name_or_name_trim', 'date_range')
    list_filter = (
        'type',
        'costs',
        'onlineOnly',
        'accessibility',
        'elixirPlatforms',
        'communities',
        'organisedByTeams',
        'organisedByOrganisations',
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
        'sponsoredBy',
    )

    date_hierarchy = 'dates__dateStart'

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                short_name_or_name=Case(
                    When(shortName='', then=F('name')),
                    When(shortName__isnull=True, then=F('name')),
                    default='shortName',
                    output_field=CharField(),
                )
            )
        )

    def short_name_or_name_trim(self, obj):
        if len(obj.short_name_or_name) <= 35:
            return obj.short_name_or_name
        return "%.32s..." % obj.short_name_or_name

    short_name_or_name_trim.short_description = "Name"
    short_name_or_name_trim.admin_order_field = 'short_name_or_name'

    def date_range(self, obj):
        start, end = (
            type(obj)
            .objects.filter(pk=obj.pk)
            .annotate(min=Min('dates__dateStart'), max=Max('dates__dateEnd'))
            .values_list('min', 'max')
            .get()
        )
        if start is None:
            return None
        if end is None:
            return dateformat.format(start, "Y-m-d")
        return f'{dateformat.format(start, "Y-m-d")} - {dateformat.format(end, "Y-m-d")}'

    date_range.short_description = "Period"
    date_range.admin_order_field = 'dates__dateStart'


@admin.register(models.Training)
class TrainingAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
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
class TopicAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ['uri', 'label', 'description', 'synonyms']
    list_display = (
        'label',
        'uri',
    )
    readonly_fields = ('label', 'description', 'synonyms')

    actions = [
        'update_information_from_ebi_ols',
        # 'update_information_from_ebi_ols_when_needed',
    ]

    def update_information_from_ebi_ols(self, request, queryset):
        for o in queryset:
            o.update_information_from_ebi_ols()


@admin.register(models.EventCost)
class EventCostAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ['cost']


@admin.register(models.EventDate)
class EventDateAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    pass


@admin.register(models.Trainer)
class TrainerAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'trainerName',
        'trainerEmail',
        'trainerId__email',
        'trainerId__firstname',
        'trainerId__lastname',
    )
    autocomplete_fields = ('trainerId',)


@admin.register(models.TrainingEventMetrics)
class TrainingEventMetricsAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'dateStart',
        'dateEnd',
        'training__name',
        'event__shortName',
        'event__description',
    )
    autocomplete_fields = ('event',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.fields['event'].queryset = models.Event.objects.filter(type=models.Event.EventType.TRAINING_COURSE)
        return form


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
class FieldAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ('field',)


@admin.register(models.Doi)
class DoiAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ('doi',)
    list_display = (
        'doi',
        'title',
        'authors_list',
        'biblio_year',
    )

    actions = [
        'update_information',
    ]
    readonly_fields = ('title', 'journal_name', 'authors_list', 'biblio_year')

    def update_information(self, request, queryset):
        for o in queryset:
            try:
                o.fill_from_doi()
                o.save()
            except BibliographicalEntryNotFound:
                self.message_user(request, f"Not found: {o.doi}", messages.INFO)
            except requests.HTTPError as he:
                self.message_user(request, f"HTTPError: {o.doi} : {str(he)}", messages.ERROR)


@admin.register(models.Project)
class ProjectAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'name',
        'homepage',
        'description',
        'topics__uri',
        'team__name',
        'hostedBy__name',
        'fundedBy__name',
        'communities__name',
        'elixirPlatforms__name',
        'uses__name',
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
class AudienceRoleAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ['audienceRole']


@admin.register(models.AudienceType)
class AudienceTypeAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = ['audienceType']


@admin.register(models.TrainingMaterial)
class TrainingMaterialAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'doi__doi',
        'fileName',
        'topics__uri',
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
        'accessibility',
    )
    save_as = True

    list_filter = ('accessibility',)

    autocomplete_fields = (
        'providedBy',
        'trainingMaterials',
    )


@admin.register(models.Team)
class TeamAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    ordering = (Upper(Unaccent("name")),)
    search_fields = (
        'name',
        'description',
        'expertise__uri',
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


# @admin.register(models.BioinformaticsTeam)
# class BioinformaticsTeamAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
#     ordering = (Unaccent("name"),)
#     search_fields = (
#         'name',
#         'description',
#         'expertise__uri',
#         'leader__firstname',
#         'leader__lastname',
#         'deputies__firstname',
#         'deputies__lastname',
#         'scientificLeaders__firstname',
#         'scientificLeaders__lastname',
#         'technicalLeaders__firstname',
#         'technicalLeaders__lastname',
#         'members__firstname',
#         'members__lastname',
#         'maintainers__firstname',
#         'maintainers__lastname',
#         'orgid',
#         'unitId',
#         'address',
#         'fields__field',
#         'keywords__keyword',
#         'communities__name',
#         'projects__name',
#         'fundedBy__name',
#         'publications__doi',
#         'certifications__name',
#     )
#
#     list_filter = ('fields',)
#
#     autocomplete_fields = (
#         'fields',
#         'platforms',
#         'communities',
#         'projects',
#     )
#     filter_horizontal = (
#         'scientificLeaders',
#         'technicalLeaders',
#         'members',
#         'maintainers',
#         'deputies',
#     )
#     list_display = (
#         'name',
#         'logo',
#     )
#
#     def logo(self, obj):
#         if obj.logo_url:
#             return format_html('<center style="margin: -8px;"><img height="32px" src="' + obj.logo_url + '"/><center>')
#         return format_html('<center style="margin: -8px;">-<center>')
#
#     logo.short_description = format_html("<center>" + ugettext("Image") + "<center>")


@admin.register(models.Service)
class ServiceAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'name',
        'description',
        'teams__name',
        'computingFacilities__name',
        'trainings__name',
        'trainingMaterials__name',
        'publications__doi',
    )

    autocomplete_fields = (
        'computingFacilities',
        'trainings',
        'trainingMaterials',
        'teams',
    )


@admin.register(models.ServiceSubmission)
class ServiceSubmissionAdmin(PermissionInClassModelAdmin, ViewInApiModelAdmin):
    search_fields = (
        'service__name',
        'authors__firstname',
        'authors__lastname',
        'submitters__firstname',
        'submitters__lastname',
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
    search_fields = (
        'name',
        'biotoolsID',
        'description',
    )
    list_filter = (
        'tool_type',
        'collection',
        'operating_system',
    )
    list_display_links = (
        'name',
        'biotoolsID',
    )
    list_display = (
        'name',
        'biotoolsID',
        'update_needed',
    )

    actions = [
        'update_information_from_biotool',
        'update_information_from_biotool_when_needed',
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(name_len=Length('name'))
            .annotate(
                update_needed=Case(
                    When(Q(name_len=0), then=True),
                    When(Q(name="None"), then=True),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        )

    def update_needed(self, obj):
        return obj.update_needed

    update_needed.boolean = True

    update_needed.admin_order_field = 'update_needed'

    def update_information_from_biotool(self, request, queryset):
        for o in queryset:
            o.update_information_from_biotool()

    def update_information_from_biotool_when_needed(self, request, queryset):
        for o in queryset.filter(update_needed=True):
            o.update_information_from_biotool()

    def get_fields(self, request, obj=None):
        if obj is None:
            return ('biotoolsID',)
        return super().get_fields(request=request, obj=obj)


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
        self.fields['users'].queryset = get_user_model().objects.filter(is_active=True)
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
class GroupAdmin(PermissionInClassModelAdmin, GroupAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']
    search_fields = (
        'user__email',
        'permissions__codename',
    )

    list_display = (
        'name',
        'permissions_count',
        'users_count',
    )

    actions = [
        'init_specific_groups',
    ]

    def init_specific_groups(self, request, queryset):
        business_logic.init_business_logic()

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(Count('permissions', distinct=True), Count('user', distinct=True))

    def permissions_count(self, obj):
        return obj.permissions__count

    permissions_count.admin_order_field = 'permissions__count'

    def users_count(self, obj):
        return obj.user__count

    users_count.admin_order_field = 'user__count'

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request=request, obj=obj) and (
            obj is None or obj.name not in business_logic.get_not_to_be_deleted_group_names()
        )

    def get_readonly_fields(self, request, obj=None):
        if obj is None or obj.name not in business_logic.get_not_to_be_deleted_group_names():
            return super().get_readonly_fields(request)
        return (
            "name",
            "permissions",
        )


# Unregister the original Token admin.
admin.site.unregister(Token)


@admin.register(Token)
class TokenAdmin(PermissionInClassModelAdmin, admin.ModelAdmin):
    list_display = ('key', 'user', 'created')
    fields = ('user',)
    ordering = ('-created',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and not business_logic.is_user_manager(None, request=request):
            qs = qs.filter(user=request.user)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request=request, obj=obj, **kwargs)
        if not request.user.is_superuser and not business_logic.is_user_manager(None, request=request):
            form.base_fields['user'].queryset = form.base_fields['user'].queryset.filter(pk=request.user.pk)
        return form

    def get_changeform_initial_data(self, request):
        return dict(user=request.user)


# register all models that are not registered yet
from django.apps import apps


class DefaultPermissionInClassModelAdmin(PermissionInClassModelAdmin):
    pass


models = apps.get_app_config('ifbcat_api').get_models()
for model in models:
    try:
        admin.site.register(model, DefaultPermissionInClassModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass
