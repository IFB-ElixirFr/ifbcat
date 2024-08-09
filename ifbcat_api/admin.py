import itertools
import re
import time

import requests
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminTextInputWidget
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.lookups import Unaccent
from django.core.exceptions import ValidationError
from django.db.models import Count, Q, When, Value, BooleanField, Case, CharField, F
from django.db.models.functions import Upper, Length
from django.forms import modelform_factory
from django.http import HttpResponseRedirect
from django.urls import reverse, NoReverseMatch
from django.utils import dateformat, timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, ngettext
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from rest_framework.authtoken.models import Token

from ifbcat_api import models, business_logic
from ifbcat_api.misc import BibliographicalEntryNotFound, get_usage_in_related_field
from ifbcat_api.model.event import Event
from ifbcat_api.permissions import simple_override_method


class ModelAdminFillingMaintainers(admin.ModelAdmin):
    class Meta:
        abstract = True

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['maintainers'] = list(get_user_model().objects.filter(pk=request.user.pk))
        return initial


class PermissionInClassModelAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    def has_view_permission(self, request, obj=None):
        with business_logic.RequestUpgrade(
            request=request,
            from_admin=True,
        ):
            from_super = super().has_view_permission(request=request, obj=obj)
            if not from_super:
                return False
            if obj is None:
                return from_super

            return business_logic.has_view_permission(model=self.model, request=request, obj=obj)

    def has_add_permission(self, request):
        with business_logic.RequestUpgrade(
            request=request,
            from_admin=True,
        ):
            from_super = super().has_add_permission(request=request)
            if not from_super:
                return False

            return business_logic.has_add_permission(model=self.model, request=request)

    def has_change_permission(self, request, obj=None):
        with business_logic.RequestUpgrade(
            request=request,
            from_admin=True,
        ):
            from_super = super().has_change_permission(request=request, obj=obj)
            if not from_super:
                return False
            if obj is None:
                return from_super

            return business_logic.has_change_permission(model=self.model, request=request, obj=obj)

    def has_delete_permission(self, request, obj=None):
        with business_logic.RequestUpgrade(
            request=request,
            from_admin=True,
        ):
            from_super = super().has_delete_permission(request=request, obj=obj)
            if not from_super:
                return False
            if obj is None:
                return from_super
            return business_logic.has_delete_permission(model=self.model, request=request, obj=obj)


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

    def render_link_view_in_api(self, obj):
        return True

    def view_in_api_in_list(self, obj):
        if not self.render_link_view_in_api(obj):
            return ""
        try:
            return format_html(
                '<center><a href="'
                + reverse('%s-detail' % obj.__class__.__name__.lower(), args=[getattr(obj, self.slug_name)])
                + '"><i class="fa fa-external-link-alt"></i></a><center>'
            )
        except NoReverseMatch:
            return format_html('<center><i class="fa fa-ban"></i></center>')

    view_in_api_in_list.short_description = format_html('<center>View in API<center>')


class AllFieldInAutocompleteModelAdmin(admin.ModelAdmin):
    class Meta:
        abstract = True

    @property
    def autocomplete_fields(self):
        return list(set([f.name for f in self.model._meta.local_many_to_many]) - set(self.filter_horizontal))


class ViewInApiModelByNameAdmin(ViewInApiModelAdmin):
    slug_name = "name"


class ViewInApiModelByBiotoolsIDAdmin(ViewInApiModelAdmin):
    slug_name = "biotoolsID"


# Models are registered below
# Enable Django admin for user profile and news item models - i.e. make them accessible through admin interface


@admin.register(models.UserProfile)
class UserProfileAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
    UserAdmin,
):
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
                'fields': ('email', 'firstname', 'lastname'),
            },
        ),
    )
    filter_horizontal = (
        "user_permissions",
        "groups",
    )
    add_form = modelform_factory(models.UserProfile, fields=('email', 'firstname', 'lastname'))

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = set(super().get_readonly_fields(request=request, obj=obj))
        if not request.user.is_superuser:
            readonly_fields |= set(itertools.chain(*[d['fields'] for _, d in self.fieldsets]))
            if obj is None:
                readonly_fields.discard("email")
            if request.user == obj:
                readonly_fields.discard("email")
                readonly_fields.discard("password")
                readonly_fields.discard("firstname")
                readonly_fields.discard("lastname")
                readonly_fields.discard("homepage")
                readonly_fields.discard("orcidid")
                readonly_fields.discard("expertise")
            if self.has_change_permission(request=request, obj=obj):
                readonly_fields.discard("firstname")
                readonly_fields.discard("lastname")
                readonly_fields.discard("homepage")
                readonly_fields.discard("orcidid")
                readonly_fields.discard("expertise")
                if obj is not None and not obj.is_superuser and not obj.is_staff:
                    readonly_fields.discard("email")
                if obj is not None and not obj.is_superuser:
                    readonly_fields.discard("groups")
                    readonly_fields.discard("is_active")
                    readonly_fields.discard("is_staff")
        return readonly_fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request=request, obj=obj)
        ret = []
        for k, f in fieldsets:
            if (
                request.user.is_superuser
                or (
                    (self.has_change_permission(request=request, obj=obj) or request.user == obj)
                    and (business_logic.is_curator(request.user) or k != 'Permissions')
                    and (request.user == obj or k != "Password")
                )
                or k in ["Personal info", "Important dates"]
            ):
                ret.append((k, f))
        return ret

    @staticmethod
    def make_revoke_group_action(group: Group, manage_is_staff: bool = False):
        def _action(modeladmin, request, qset):
            updated = 0
            count = 0
            for o in qset:
                if business_logic.can_edit_user(request.user, o):
                    fields = []
                    count += 1
                    updated_count = qset.filter(groups=group).filter(pk=o.pk).count()
                    updated += updated_count
                    if updated_count == 1:
                        fields.append('groups')
                    o.groups.remove(group)
                    if manage_is_staff and o.is_staff:
                        o.is_staff = False
                        fields.append('is_staff')
                        o.save()
                    if fields:
                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=ContentType.objects.get_for_model(o).pk,
                            object_id=o.id,
                            object_repr=str(o),
                            action_flag=CHANGE,
                            change_message=[{"changed": {"fields": fields}}],
                        )
            already_there = count - updated
            if updated == 0:
                modeladmin.message_user(
                    request,
                    'All were already out of the group "%s"' % group.name,
                    messages.WARNING,
                )
            else:
                msg = (
                    ngettext(
                        '%(d)d user was successfully removed from group "%(s)s".',
                        '%(d)d user were successfully removed from group "%(s)s".',
                        updated,
                    )
                    % dict(d=updated, s=group.name)
                )
                if already_there > 0:
                    msg += (
                        ngettext(
                            '(and %d was already absent)',
                            '(and %d were already absent)',
                            already_there,
                        )
                        % already_there
                    )
                modeladmin.message_user(
                    request,
                    msg,
                    messages.SUCCESS,
                )

        name = 'revoke_%s' % re.sub('[\W]+', '_', str(group))
        return name, (_action, name, 'Revoke permissions "%s"' % group)

    @staticmethod
    def make_grant_group_action(group: Group, manage_is_staff: bool = False):
        def _action(modeladmin, request, qset):
            already_there = 0
            not_staff = 0
            count = 0
            for o in qset:
                if business_logic.can_edit_user(request.user, o):
                    fields = []
                    is_already_there_count = qset.filter(groups=group).filter(pk=o.pk).count()
                    if is_already_there_count == 0:
                        fields.append('groups')
                    already_there += is_already_there_count
                    count += 1
                    o.groups.add(group)
                    if manage_is_staff:
                        if not o.is_active or not o.is_staff:
                            not_staff += 1
                            if not o.is_active:
                                fields.append('is_active')
                            if not o.is_staff:
                                fields.append('is_staff')
                            o.is_active = True
                            o.is_staff = True
                            o.save()
                    if fields:
                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=ContentType.objects.get_for_model(o).pk,
                            object_id=o.id,
                            object_repr=str(o),
                            action_flag=CHANGE,
                            change_message=[{"changed": {"fields": fields}}],
                        )
            if not_staff > 0:
                modeladmin.message_user(
                    request,
                    "%i users have been newly granted access to the admin UI" % not_staff,
                    messages.SUCCESS,
                )
            updated = count - already_there
            if updated == 0:
                modeladmin.message_user(
                    request,
                    'All were already in the group "%s"' % group.name,
                    messages.WARNING,
                )
            else:
                msg = (
                    ngettext(
                        '%(d)d user was successfully add to group "%(s)s"',
                        '%(d)d user where successfully add to group "%(s)s"',
                        updated,
                    )
                    % dict(d=updated, s=group.name)
                )
                if already_there > 0:
                    msg += (
                        ngettext(
                            '(and %d was already associated)',
                            '(and %d were already associated)',
                            already_there,
                        )
                        % already_there
                    )
                modeladmin.message_user(
                    request,
                    msg + ".",
                    messages.SUCCESS,
                )

        name = 'grant_%s' % re.sub('[\W]+', '_', str(group))
        return name, (_action, name, 'Grant permissions "%s"' % group)

    @staticmethod
    def get_group_actions():
        groups = Group.objects.filter(
            name__in=set(business_logic.get_not_to_be_deleted_group_names())
            - {business_logic.get_no_restriction_group_name()}
        ).order_by('name')
        return dict(
            itertools.chain(
                [
                    UserProfileAdmin.make_grant_group_action(
                        group=o,
                        manage_is_staff=o.name == business_logic.get_basic_permissions_group_name(),
                    )
                    for o in groups
                ],
                [
                    UserProfileAdmin.make_revoke_group_action(
                        group=o,
                        manage_is_staff=o.name == business_logic.get_basic_permissions_group_name(),
                    )
                    for o in groups
                ],
            )
        )

    @classmethod
    def get_static_actions(cls, request):
        if (
            request is None
            or not business_logic.is_curator(request.user)
            or not business_logic.is_user_manager(request.user)
        ):
            return {}
        return dict(
            **cls.get_group_actions(),
        )

    def get_actions(self, request):
        actions = super().get_actions(request=request)
        actions.update(self.get_static_actions(request=request))
        return actions


# "search_fields" defines the searchable 'fields'
# "list_filter" adds fields to Django admin filter box
# "filter_horizontal" adds widgets for item selection from lists
@admin.register(models.Event)
class EventAdmin(
    ModelAdminFillingMaintainers,
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
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
        'contacts__email',
        'organisedByTeams__name',
        'organisedByOrganisations__name',
        'sponsoredBy__name',
        'sponsoredBy__organisationId__name',
    )
    save_as = True
    list_display = (
        'short_name_or_name_trim',
        'logo',
        'date_range',
        'is_tess_publishing',
    )
    list_filter = (
        'type',
        'costs',
        'courseMode',
        'is_draft',
        'openTo',
        'elixirPlatforms',
        'communities',
        'organisedByTeams',
        'organisedByOrganisations',
        'tess_publishing',
        'training',
    )
    #
    filter_horizontal = ()
    fieldsets = (
        (
            'Event info',
            {
                'fields': (
                    'name',
                    'shortName',
                    'description',
                    'is_draft',
                    'type',
                    'logo_url',
                    'homepage',
                    'keywords',
                    'topics',
                    'tess_publishing',
                    'maintainers',
                )
            },
        ),
        (
            'Dates',
            {
                'fields': (
                    'registration_opening',
                    'registration_closing',
                    'start_date',
                    'end_date',
                )
            },
        ),
        (
            'Location',
            {
                'fields': (
                    'streetAddress',
                    'postalCode',
                    'city',
                    'country',
                    'courseMode',
                    'venue',
                )
            },
        ),
        (
            'Audience',
            {
                'fields': (
                    'maxParticipants',
                    'openTo',
                    'accessConditions',
                    'costs',
                    'geographical_range',
                )
            },
        ),
        (
            'Organizers and sponsors',
            {
                'fields': (
                    'contacts',
                    'organisedByOrganisations',
                    'organisedByTeams',
                    'sponsoredBy',
                    'elixirPlatforms',
                    'trainers',
                )
            },
        ),
        (
            'Content',
            {
                'fields': (
                    'prerequisites',
                    'communities',
                    'computingFacilities',
                    'training',
                    'trainingMaterials',
                    'hoursPresentations',
                    'hoursHandsOn',
                    'hoursTotal',
                )
            },
        ),
    )
    date_hierarchy = 'start_date'

    def render_link_view_in_api(self, obj):
        return not obj.is_draft

    def logo(self, obj):
        if obj.logo_url:
            return format_html('<center style="margin: -8px;"><img height="32px" src="' + obj.logo_url + '"/><center>')
        return format_html('<center style="margin: -8px;">-<center>')

    logo.short_description = format_html("<center>" + gettext("Logo") + "<center>")

    def get_queryset(self, request):
        return Event.annotate_is_tess_publishing(super().get_queryset(request)).annotate(
            short_name_or_name=Case(
                When(shortName='', then=F('name')),
                When(shortName__isnull=True, then=F('name')),
                default='shortName',
                output_field=CharField(),
            )
        )

    def short_name_or_name_trim(self, obj):
        if len(obj.short_name_or_name) <= 99:
            return obj.short_name_or_name
        return "%.96s..." % obj.short_name_or_name

    short_name_or_name_trim.short_description = "Name"
    short_name_or_name_trim.admin_order_field = 'short_name_or_name'

    def is_tess_publishing(self, obj):
        s = ''
        if obj.tess_publishing == 2:
            s += '<i class="fa fa-magic text-muted" title="Automatically computed"></i> '
        if obj.is_tess_publishing:
            s += '<i class="fa fa-check text-success" title="Is published"></i>'
        else:
            s += '<i class="fa fa-times" title="Is NOT published"></i>'
        return format_html('<center>' + s + '</center>')

    is_tess_publishing.short_description = format_html("<center>TESS sync</center>")
    is_tess_publishing.admin_order_field = 'short_name_or_name'

    def date_range(self, obj):
        start, end = obj.start_date, obj.end_date
        if start is None:
            return None
        if end is None:
            return dateformat.format(start, "Y-m-d")
        return f'{dateformat.format(start, "Y-m-d")} - {dateformat.format(end, "Y-m-d")}'

    date_range.short_description = "Period"
    date_range.admin_order_field = 'start_date'


@admin.register(models.Training)
class TrainingAdmin(
    ModelAdminFillingMaintainers,
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    save_as = True
    list_display = (
        "name",
        "logo",
        "home",
    )
    search_fields = (
        'name',
        'shortName',
        'description',
        # 'topics__uri',
        'keywords__keyword',
        # 'prerequisites__prerequisite',
        # 'accessConditions',
        'contacts__email',
        # 'organisedByTeams__name',
        # 'organisedByOrganisations__name',
        # 'sponsoredBy__name',
        # 'sponsoredBy__organisationId__name',
    ) + (
        # 'audienceTypes__audienceType',
        # 'audienceRoles__audienceRole',
        # 'difficultyLevel',
        # 'learningOutcomes',
    )
    list_filter = (
        'trainingMaterials',
        'computingFacilities',
        'organisedByTeams',
        'organisedByOrganisations',
        'sponsoredBy',
        'is_draft',
        'openTo',
        'costs',
        'tess_publishing',
        # 'databases',
        # 'tools',
    )
    fieldsets = (
        (
            'Training info',
            {
                'fields': (
                    'name',
                    'shortName',
                    'description',
                    'is_draft',
                    'logo_url',
                    'homepage',
                    'topics',
                    'keywords',
                    'tess_publishing',
                    'maintainers',
                )
            },
        ),
        (
            'Audience',
            {
                'fields': (
                    'maxParticipants',
                    'openTo',
                    'accessConditions',
                    'costs',
                    'personalised',
                    'audienceTypes',
                    'audienceRoles',
                )
            },
        ),
        (
            'Organizers and sponsors',
            {
                'fields': (
                    'contacts',
                    'organisedByOrganisations',
                    'organisedByTeams',
                    'elixirPlatforms',
                    'sponsoredBy',
                )
            },
        ),
        (
            'Content',
            {
                'fields': (
                    'prerequisites',
                    'communities',
                    'computingFacilities',
                    'difficultyLevel',
                    'learningOutcomes',
                    'trainingMaterials',
                    'hoursPresentations',
                    'hoursHandsOn',
                    'hoursTotal',
                )
            },
        ),
    )
    actions = ["create_new_course"]

    def render_link_view_in_api(self, obj):
        return not obj.is_draft

    @staticmethod
    def create_new_course_and_get_admin_url(request, training):
        course = training.create_new_event(None, None)
        course.maintainers.add(request.user)
        messages.success(request, "A draft for a new session have been created, you can now update it, or delete it.")

        courseModel = course._meta.model

        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(courseModel).pk,
            object_id=course.id,
            object_repr=str(course),
            action_flag=ADDITION,
        )

        opts = courseModel._meta
        redirect_url = reverse(
            'admin:%s_%s_change' % (opts.app_label, opts.model_name),
            args=(course.pk,),
        )
        return course, redirect_url

    @admin.action(description='Create new session')
    def create_new_course(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Can only create a new session/event one training at a time", messages.ERROR)
            return
        course, url = self.create_new_course_and_get_admin_url(request=request, training=queryset.first())
        self.message_user(
            request, mark_safe(f'New session created, go to <a href="{url}">{url}</a> to complete it'), messages.SUCCESS
        )

    def logo(self, obj):
        if not obj.logo_url:
            return ''
        return format_html('<center style="margin: -8px;"><img height="32px" src="' + obj.logo_url + '"/><center>')

    def home(self, obj):
        if not obj.homepage:
            return ""
        return format_html(
            '<center><a target="_blank" href="' + obj.homepage + '"><i class="fa fa-home"></i></a><center>'
        )

    home.short_description = format_html('<center>homepage</center>')


@admin.register(models.Keyword)
class KeywordAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ['keyword']

    actions = [
        'split_by_comma_and_remove',
        'merge_other_where_only_case_differs',
    ]

    def get_actions(self, request):
        actions = super().get_actions(request=request)
        if not business_logic.is_curator(request.user):
            if 'split_by_comma_and_remove' in actions:
                del actions['split_by_comma_and_remove']
            if 'merge_other_where_only_case_differs' in actions:
                del actions['merge_other_where_only_case_differs']
        return actions

    def merge_other_where_only_case_differs(self, request, queryset):
        attrs = get_usage_in_related_field(queryset)
        studied = set()
        to_remove = set()
        for o in queryset:
            if o.id in studied:  # ignore if already seen, to prevent cross removal
                continue
            studied.add(o.id)
            for other in queryset.model.objects.filter(keyword__icontains=o.keyword.strip()).exclude(id=o.id).all():
                if other.keyword.strip().casefold() != o.keyword.strip().casefold():
                    continue
                studied.add(other.id)
                to_remove.add(other)
                for model_field, attr_name, reverse_name in attrs:
                    for r in getattr(other, attr_name).all():
                        getattr(r, reverse_name).add(o)
        for o in to_remove:
            o.delete()

    def split_by_comma_and_remove(self, request, queryset):
        attrs = get_usage_in_related_field(queryset)
        studied = set()
        to_remove = set()
        for o in queryset.filter(keyword__contains=",").exclude(keyword__contains="("):
            if o.id in studied:  # ignore if already seen, to prevent cross removal
                continue
            studied.add(o.id)
            to_remove.add(o)
            for model_field, attr_name, reverse_name in attrs:
                sub_keywords = []
                for k in o.keyword.split(','):
                    sub_keyword = queryset.model.objects.filter(keyword__iexact=k.strip()).first()
                    if sub_keyword is None:
                        sub_keyword = queryset.model.objects.create(keyword=k.strip())
                    sub_keywords.append(sub_keyword)
                for r in getattr(o, attr_name).all():
                    reverse_attr = getattr(r, reverse_name)
                    for k in sub_keywords:
                        studied.add(k.id)
                        reverse_attr.add(k)
        for o in to_remove:
            o.delete()
        return True


@admin.register(models.EventPrerequisite)
class EventPrerequisiteAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ['prerequisite']


@admin.register(models.Topic)
class TopicAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ['uri', 'label', 'description', 'synonyms']
    list_display = (
        'label',
        'uri_browser',
    )
    readonly_fields = ('label', 'description', 'synonyms')

    actions = [
        'update_information_from_ebi_ols',
        # 'update_information_from_ebi_ols_when_needed',
    ]

    def update_information_from_ebi_ols(self, request, queryset):
        for o in queryset:
            o.update_information_from_ebi_ols()

    def uri_browser(self, obj):
        return format_html(f'<center><a href="{obj.edam_browser_url}" target="_blank">{obj.uri}</a></center>')

    uri_browser.short_description = format_html("<center>" + gettext("URI") + "<center>")


@admin.register(models.EventCost)
class EventCostAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ['cost']


@admin.register(models.TrainingCourseMetrics)
class TrainingCourseMetricsAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = (
        'dateStart',
        'dateEnd',
        'event__name',
        'event__shortName',
        'event__description',
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['event'].queryset = Event.objects.filter(type=Event.EventType.TRAINING_COURSE)
        return form


@admin.register(models.EventSponsor)
class EventSponsorAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = (
        'name',
        'organisationId__name',
    )


@admin.register(models.Certification)
class CertificationAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = (
        'name',
        'description',
    )


@admin.register(models.Community)
class CommunityAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = (
        'name',
        'description',
        'homepage',
        'organisations__name',
    )


@admin.register(models.ElixirPlatform)
class ElixirPlatformAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
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
class OrganisationAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelByNameAdmin,
):
    search_fields = (
        'name',
        'description',
        'homepage',
        'orgid',
        'fields__field',
        'city',
    )
    list_filter = ('fields',)


@admin.register(models.Field)
class FieldAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ('field',)


@admin.register(models.Doi)
class DoiAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ('doi', 'title', 'authors_list')
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
class ProjectAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
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


@admin.register(models.AudienceRole)
class AudienceRoleAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ['audienceRole']


@admin.register(models.AudienceType)
class AudienceTypeAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ['audienceType']


@admin.register(models.TrainingMaterial)
class TrainingMaterialAdmin(
    ModelAdminFillingMaintainers,
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelByNameAdmin,
):
    save_as = True
    search_fields = (
        'name',
        'description',
        'doi__doi',
        'fileName',
        'fileLocation',
        'topics__uri',
        'topics__label',
        'keywords__keyword',
        'audienceTypes__audienceType',
        'audienceRoles__audienceRole',
        'difficultyLevel',
        'providedBy__name',
    )


@admin.register(models.ComputingFacility)
class ComputingFacilityAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelByNameAdmin,
):
    search_fields = (
        'homepage',
        'providedBy__name',
        'accessibility',
    )
    save_as = True

    list_filter = ('accessibility',)


class TeamForm(forms.ModelForm):
    class Meta:
        model = models.Team
        widgets = {
            'lng': AdminTextInputWidget(),
            'lat': AdminTextInputWidget(),
        }
        fields = '__all__'

    publications_batch = forms.CharField(
        help_text="List of DOI to add to the current Team, one per line.",
        required=False,
        widget=forms.widgets.Textarea(attrs={'row': 10, 'class': 'vLargeTextField'}),
    )
    osm_link = forms.URLField(
        label="Location on a map",
        help_text="Link to view this gps coordinate in OpenStreetMap",
        widget=AdminTextInputWidget(),
        required=False,
    )

    def __init__(self, *args, instance=None, initial=None, **kwargs):
        if initial is None:
            initial = dict()
        if instance is not None:
            initial["osm_link"] = instance.get_osm_link()
        super().__init__(*args, initial=initial, instance=instance, **kwargs)
        self.fields['osm_link'].widget.attrs["disabled"] = True

    def _save_m2m(self):
        super()._save_m2m()
        for doi_str in self.cleaned_data["publications_batch"].split('\n'):
            doi_str = doi_str.strip()
            doi, _ = models.Doi.objects.get_or_create(doi=doi_str)
            self.instance.publications.add(doi)


class IsActiveListFilter(admin.SimpleListFilter):
    title = 'Is active'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ("True", "True"),
            ("False", "False"),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(is_active=self.value() == "True")


@admin.register(models.Team)
class TeamAdmin(
    ModelAdminFillingMaintainers,
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelByNameAdmin,
):
    form = TeamForm
    ordering = (Upper(Unaccent("name")),)
    search_fields = (
        'name',
        'description',
        'expertise__uri',
        'leaders__firstname',
        'leaders__lastname',
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
    filter_horizontal = (
        # 'scientificLeaders',
        # 'technicalLeaders',
        # 'members',
        # 'maintainers',
        # 'deputies',
    )
    list_display = (
        'name',
        'logo',
        'updated_at',
    )
    list_filter = (
        IsActiveListFilter,
        'ifbMembership',
    )
    fieldsets = (
        (
            'Team info',
            {
                'fields': (
                    'name',
                    'description',
                    'orgid',
                    'homepage',
                    'logo_url',
                    'maintainers',
                    'closing_date',
                )
            },
        ),
        (
            'Location',
            {
                'fields': (
                    'address',
                    'postalCode',
                    'city',
                    'country',
                    'lat',
                    'lng',
                    'osm_link',
                )
            },
        ),
        (
            'Skills',
            {
                'fields': (
                    'fields',
                    'keywords',
                    'expertise',
                    'certifications',
                    'linkCovid19',
                )
            },
        ),
        (
            'Results',
            {
                'fields': (
                    'tools',
                    'publications',
                    'publications_batch',
                )
            },
        ),
        (
            'Persons',
            {
                'fields': (
                    'leaders',
                    'scientificLeaders',
                    'technicalLeaders',
                    'deputies',
                    'members',
                )
            },
        ),
        (
            'Organisations',
            {
                'fields': (
                    'unitId',
                    'communities',
                    'projects',
                    'fundedBy',
                    'affiliatedWith',
                    'ifbMembership',
                    'platforms',
                )
            },
        ),
    )

    actions = [
        'guess_coordinate_from_address',
        'guess_coordinate_from_address_when_needed',
    ]

    def guess_coordinate_from_address_when_needed(self, request, queryset):
        queryset = queryset.filter(lat__isnull=True)
        if not queryset.exists():
            messages.info(
                request,
                'No team without coordinates were found in selected teams',
            )
        return self.guess_coordinate_from_address(request=request, queryset=queryset)

    def guess_coordinate_from_address(self, request, queryset):
        if queryset.count() > 3:
            messages.warning(
                request,
                'Too many teams selected at once, working only on the top three first',
            )
        first = True
        for o in queryset.all()[:3]:
            if not first:
                time.sleep(2)
            if o.guess_coordinate_from_address():
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(o).pk,
                    object_id=o.id,
                    object_repr=str(o),
                    action_flag=CHANGE,
                    change_message=[{"changed": {"fields": ['lon', 'lar']}}],
                )
                messages.success(
                    request,
                    mark_safe(
                        f'Coordinate of "{o}" guessed at '
                        f'<a target="_blank" href="{o.get_osm_link()}">{o.get_osm_link()}</a>'
                    ),
                )
            else:
                messages.warning(
                    request,
                    f'Could not guess coordinate of "{o}"',
                )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request=request)
            .annotate(
                is_active=Case(
                    When(Q(closing_date__lt=timezone.now()), then=Value(False)),
                    default=Value(True),
                    output_field=BooleanField(),
                )
            )
        )

    def logo(self, obj):
        if obj.logo_url:
            return format_html('<center style="margin: -8px;"><img height="32px" src="' + obj.logo_url + '"/><center>')
        return format_html('<center style="margin: -8px;">-<center>')

    logo.short_description = format_html("<center>" + gettext("Image") + "<center>")


class AbstractControlledVocabularyAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = ('name',)


admin.site.register(models.ServiceDomain, AbstractControlledVocabularyAdmin)
admin.site.register(models.ServiceCategory, AbstractControlledVocabularyAdmin)
admin.site.register(models.LifeScienceCommunity, AbstractControlledVocabularyAdmin)
admin.site.register(models.KindOfAnalysis, AbstractControlledVocabularyAdmin)


@admin.register(models.Service)
class ServiceAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelAdmin,
):
    search_fields = (
        'domain__name',
        'category__name',
        'analysis__name',
        'team__name',
        'communities__name',
        'comments',
    )
    list_filter = (
        'domain',
        'category',
        'analysis',
        'team',
        'communities',
        'training',
        'collaboration',
        'prestation',
    )
    list_display = (
        'domain',
        'category',
        'analysis',
        'team',
        'training',
        'collaboration',
        'prestation',
    )
    fieldsets = (
        (
            '',
            {
                'fields': (
                    'team',
                    'domain',
                    'category',
                    'analysis',
                    'communities',
                )
            },
        ),
        (
            '',
            {
                'fields': (
                    'training',
                    'mentoring',
                    'collaboration',
                    'prestation',
                    'comments',
                )
            },
        ),
    )


class ToolAdminForm(forms.ModelForm):
    class Meta:
        model = models.Tool
        fields = ('biotoolsID',)

    def is_valid(self):
        if not super().is_valid():
            return False
        self.instance.json_from_biotool = self.instance.fetch_json_from_biotool()
        if models.Tool.objects.filter(biotoolsID__iexact=self.instance.json_from_biotool['biotoolsID']).exists():
            self.add_error('biotoolsID', 'biotoolsID already present in the database')
            return False
        return True


@admin.register(models.Tool)
class ToolAdmin(
    PermissionInClassModelAdmin,
    AllFieldInAutocompleteModelAdmin,
    ViewInApiModelByBiotoolsIDAdmin,
):
    search_fields = (
        'name',
        'biotoolsID',
        'tool_licence__name',
        'description',
    )
    list_filter = (
        'tool_type',
        'tool_licence',
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
        # 'update_needed',
    )

    form = ToolAdminForm

    actions = [
        'update_information_from_biotool',
        # 'update_information_from_biotool_when_needed',
    ]

    # def get_queryset(self, request):
    #     return (
    #         super()
    #         .get_queryset(request)
    #         .annotate(name_len=Length('name'))
    #         .annotate(
    #             update_needed=Case(
    #                 When(Q(name_len=0), then=True),
    #                 When(Q(name="None"), then=True),
    #                 default=Value(False),
    #                 output_field=BooleanField(),
    #             )
    #         )
    #     )
    #
    # def update_needed(self, obj):
    #     return obj.update_needed
    #
    # update_needed.boolean = True
    #
    # update_needed.admin_order_field = 'update_needed'

    def update_information_from_biotool(self, request, queryset):
        for o in queryset:
            o.update_information_from_biotool()

    # def update_information_from_biotool_when_needed(self, request, queryset):
    #     for o in queryset.filter(update_needed=True):
    #         o.update_information_from_biotool()


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
class GroupAdmin(
    PermissionInClassModelAdmin,
    GroupAdmin,
):
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
# admin.site.unregister(Token)


@admin.register(Token)
class TokenAdmin(
    PermissionInClassModelAdmin,
    admin.ModelAdmin,
):
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


class DefaultPermissionInClassModelAdmin(
    PermissionInClassModelAdmin,
):
    pass


@admin.register(models.Collection)
class CollectionAdmin(
    PermissionInClassModelAdmin,
):
    search_fields = ('name',)


@admin.register(models.OperatingSystem)
class CollectionAdmin(
    PermissionInClassModelAdmin,
):
    search_fields = ('name',)


@admin.register(models.TypeRole)
class CollectionAdmin(
    PermissionInClassModelAdmin,
):
    search_fields = ('name',)


@admin.register(models.ToolCredit)
class CollectionAdmin(
    PermissionInClassModelAdmin,
):
    search_fields = ('name',)


@admin.register(models.ToolType)
class CollectionAdmin(
    PermissionInClassModelAdmin,
):
    search_fields = ('name',)


@admin.register(models.Licence)
class LicenceAdmin(
    PermissionInClassModelAdmin,
):
    search_fields = ['name']


all_models = apps.get_app_config('ifbcat_api').get_models()
for model in all_models:
    try:
        admin.site.register(model, DefaultPermissionInClassModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass
