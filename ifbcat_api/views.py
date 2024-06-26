# Imports
#
# "Response" is used to return responses from APIView
# "status" object holds HTTP status codes - used when returning responses from the API
# TokenAuthentication is used to users to authenticate themselves with the API
# "filters" is for filtering the ViewSets
# "ObtainAuthToken" is a view used to generate an auth token
# "api_settings" is used when configuring the custom ObtainAuthToken view
# "IsAuthenticatedOrReadOnly" is used to ensure that a ViewSet is read-only if the user is not autheticated.
# "IsAuthenticated" is used to block access to an entire ViewSet endpoint unless a user is autheticated
import json

import markdown
import rest_framework.parsers
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, get_permission_codename
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.text import capfirst
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters import rest_framework as django_filters
from markdown import markdown
from rest_framework import pagination
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from ifbcat_api import models, business_logic, misc
from ifbcat_api import serializers
from ifbcat_api.admin import TrainingAdmin
from ifbcat_api.filters import AutoSubsetFilterSet


class CachedNoPaginationMixin:
    @property
    def paginator(self):
        return None

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.clear()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.clear()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.clear()

    # @method_decorator(cache_page(int(60 * 60 * 0.5)))
    @method_decorator(vary_on_cookie)
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)


def CachedNoPaginationFactory(base):
    class _tmp(CachedNoPaginationMixin, base):
        pass

    _tmp.__name__ = base.__name__ + "CNP"
    return _tmp


class PermissionInClassModelViewSet:
    class Meta:
        abstract = True

    @property
    def permission_classes(self):
        return business_logic.get_permission_classes(self.queryset.model)


class SourceInfoViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            with open("source_info.json", "r") as stream:
                info = json.load(stream)
                info["commit_url"] = "https://github.com/IFB-ElixirFr/ifbcat/commit/%s" % info["commit_sha"]
                return Response(info)
        except FileNotFoundError as e:
            return Response(str(e))


class MultipleFieldLookupMixin:
    """
    https://stackoverflow.com/a/63779871/2144569
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.

    Source: https://www.django-rest-framework.org/api-guide/generic-views/#creating-custom-mixins
    Modified to not error out for not providing all fields in the url.
    """

    def get_object(self):
        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            field_key = field
            if field[-8:] == "__iexact":
                field_key = field[:-8]
            if field[-10:] == "__endswith":
                field_key = field[:-10]
            if self.kwargs.get(field_key):  # Ignore empty fields.
                filter[field] = self.kwargs[field_key]
        obj = get_object_or_404(queryset, **filter)  # Lookup the object
        self.check_object_permissions(self.request, obj)
        return obj


# TestApiView is just a test API View - not currently used but kept in case it's needed later.
class TestApiView(APIView):
    """Test API View.  Currently just returns a test message."""

    serializer_class = serializers.TestApiViewSerializer

    # format=None can be updated if support for other formats is required in future.
    def get(self, request, format=None):
        """Returns a test message."""
        msg = ["Test message."]

        return Response({'message': msg})

    def post(self, request):
        """Creates a test message."""
        # "self.serializer_class" function retrieves the serializer class configured above
        # "data=request.data" assigns the data passed in from the POST request, to the serializer
        serializer = self.serializer_class(data=request.data)

        # is_valid() function valdates the data as per the definition in serializers.py (where "testinput" is defined)
        if serializer.is_valid():
            testinput = serializer.validated_data.get('testinput')
            message = f'Test input was: {testinput}'
            return Response({'message': message})
        else:
            # "serializer.errors" is dictionary of errors generated by the serializer.
            # Good to return this to the user in case they submitted an invlid response.
            # 400 is the standard response code for this sort of error.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # "pk=None" defaults the primary key to none (normally the ID of the object being updated is specified)
    def put(self, request, pk=None):
        """Dummy "put" method (to update an object)."""
        return Response({'method called': 'PUT'})

    def patch(self, request, pk=None):
        """Dummy "patch" method (for partial update of an object)."""
        return Response({'method called': 'PATCH'})

    def delete(self, request, pk=None):
        """Dummy "delete" method (to delete an object)."""
        return Response({'method called': 'DELETE'})


# TestViewSet is just a test API ViewSet - not currently used but kept in case it's needed later.
class TestViewSet(viewsets.ViewSet):
    """Test API ViewSet.  Currently just returns a test message."""

    # Note - reusing the serializer that was used for the "TestApiView" APIView - this is OK!
    serializer_class = serializers.TestApiViewSerializer

    # "list" method returns list of objects.  The list request corresponds to the root of the API.
    def list(self, request):
        """Dummy "list" method (to list set of objects that ViewSet represents)"""
        message = [
            "Test message for list method on APIViewSet.",
        ]

        return Response({'message': message})

    # "create" method is used to create new objects
    def create(self, request):
        """Dummy "create" method (to create a new object)"""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            testinput = serializer.validated_data.get('testinput')
            message = f'testinput: {testinput}'
            return Response({'message': message})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # "retrieve" function is for retrieving a specific object in the ViewSet
    # A primary key (pk) ID is passed into the URL / request
    def retrieve(self, request, pk=None):
        """Dummy "retrieve" function (to get an object by its ID)"""
        return Response({'http_method:': 'GET'})

    # "update" function is for updating a specific object in the ViewSet
    # A primary key (pk) ID is  passed into the URL / request
    def update(self, request, pk=None):
        """Dummy "update" function (to update an object)"""
        return Response({'http_method:': 'PUT'})

    # "partial_update" function is for partially updating a specific object in the ViewSet
    # A primary key (pk) ID is passed into the URL / request
    def partial_update(self, request, pk=None):
        """Dummy "partial_update" function (to partially update an object)"""
        return Response({'http_method:': 'PATCH'})

    # "destroy" function is for deleting a specific object in the ViewSet
    # A primary key (pk) ID is passed into the URL / request
    def destroy(self, request, pk=None):
        """Dummy "destroy" function (to delete an object)"""
        return Response({'http_method:': 'DELETE'})


# UserProfile ViewSet
# This is a ModelViewSet (which are bundled with functionality for managing models through the API)
# They're wired to a serializer class, and a query set is provided so it knows which objects
# in the DB are managed through this ViewSet
# Django REST takes care of create, list, update etc. functions on the ViewSet
class UserProfileViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handle creating and updating user profiles."""

    queryset = models.UserProfile.objects.all()
    ordering_fields = [
        'lastname',
        'firstname',
    ]
    # filter_backends adds ability to search profiles by name or email (via filtering)
    # search_fields specifies which fields are searchable by this filter.
    search_fields = (
        'firstname',
        'lastname',
        'email',
        'orcidid',
        'expertise__uri',
    )
    filterset_fields = (
        'expertise',
        'teamsLeaders',
        'teamsMembers',
        'elixirPlatformDeputies',
        'elixirPlatformCoordinator',
    )

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.UserProfileSerializerTiny
        return serializers.UserProfileSerializer

    def get_serializer_context(self):
        return dict(
            hide_id=not self.request.user.is_authenticated,
            **super().get_serializer_context(),
        )


# Class for handling user authentication.
# ObtainAuthToken has to be customised so that is enabled in the Django admin site
# (this is not not enabled by default)
class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication tokens."""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class EventFilter(AutoSubsetFilterSet):
    min_start = django_filters.DateFilter(field_name="start_date", lookup_expr='gte')
    max_start = django_filters.DateFilter(field_name="start_date", lookup_expr='lte')
    registration_status = django_filters.ChoiceFilter(
        field_name="registration_status",
        label="Registration status",
        choices=(
            ('future', 'future'),
            ('open', 'open'),
            ('unknown', 'unknown'),
            ('closed', 'closed'),
        ),
    )
    realisation_status = django_filters.ChoiceFilter(
        field_name="realisation_status",
        label="Realisation status",
        choices=(
            ('future', 'future'),
            ('past', 'past'),
            ('ongoing', 'ongoing'),
        ),
    )

    class Meta:
        model = models.Event
        fields = [
            'type',
            'min_start',
            'max_start',
            'costs',
            'topics',
            'keywords',
            'prerequisites',
            'elixirPlatforms',
            'communities',
            'organisedByTeams',
            'organisedByOrganisations',
            'sponsoredBy',
            'is_draft',
            'courseMode',
        ]


class TrainingFilter(AutoSubsetFilterSet):
    # min_start = django_filters.DateFilter(field_name="dates__dateStart", lookup_expr='gte')
    # max_start = django_filters.DateFilter(field_name="dates__dateStart", lookup_expr='lte')

    class Meta:
        model = models.Training
        fields = [
            # 'type',
            # 'min_start',
            # 'max_start',
            'costs',
            'topics',
            'keywords',
            'prerequisites',
            'elixirPlatforms',
            'communities',
            'organisedByTeams',
            'organisedByOrganisations',
            'sponsoredBy',
            'computingFacilities',
        ]


# Model ViewSet for events
class AbstractEventViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    search_fields_from_abstract_event = (
        'name',
        'shortName',
        'description',
        'costs__cost',
        'topics__uri',
        'keywords__keyword',
        'prerequisites__prerequisite',
        'openTo',
        'accessConditions',
        'contacts__email',
        'elixirPlatforms__name',
        'communities__name',
        'organisedByTeams__name',
        'organisedByOrganisations__name',
        'sponsoredBy__name',
        'sponsoredBy__organisationId__name',
    )


class EventViewSet(AbstractEventViewSet):
    """Handles creating, reading and updating events."""

    # renderer_classes = [BrowsableAPIRenderer, JSONRenderer, JsonLDSchemaTrainingRenderer]
    serializer_class = serializers.EventSerializer
    ordering = [
        '-start_date',
    ]

    queryset = models.Event.objects.filter(is_draft=False)
    search_fields = AbstractEventViewSet.search_fields_from_abstract_event + (
        'type',
        'venue',
        'city',
        'country',
        'trainers__email',
    )
    filterset_class = EventFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = models.Event.annotate_registration_realisation_status(queryset)
        return queryset

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for training
class TrainingViewSet(AbstractEventViewSet):
    """Handles creating, reading and updating training events."""

    serializer_class = serializers.TrainingSerializer
    queryset = models.Training.objects.filter(is_draft=False)

    search_fields = EventViewSet.search_fields_from_abstract_event + (
        'audienceTypes__audienceType',
        'audienceRoles__audienceRole',
        'difficultyLevel',
        'learningOutcomes',
    )
    filterset_class = TrainingFilter


# Model ViewSet for keywords
class KeywordViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating keywords."""

    serializer_class = serializers.KeywordSerializer
    retrieve_serializer_class = serializers.KeywordDetailedSerializer
    queryset = models.Keyword.objects.all()
    # lookup_field = 'keyword__unaccent__iexact'
    search_fields = ('keyword',)

    def perform_create(self, serializer):
        """Saves the serializer."""
        serializer.save()

    def get_serializer(self, *args, **kwargs):
        if self.action == "retrieve":
            kwargs['context'] = self.get_serializer_context()
            return self.retrieve_serializer_class(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)


# Model ViewSet for event prerequisites
class EventPrerequisiteViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating event prerequisites."""

    serializer_class = serializers.EventPrerequisiteSerializer
    queryset = models.EventPrerequisite.objects.all()
    search_fields = ('prerequisite',)

    def perform_create(self, serializer):
        """Saves the serializer."""
        serializer.save()


# Model ViewSet for training event metrics
class TrainingCourseMetricsViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating training event metrics."""

    serializer_class = serializers.TrainingCourseMetricsSerializer
    queryset = models.TrainingCourseMetrics.objects.all()
    search_fields = (
        'dateStart',
        'dateEnd',
        'event__name',
        'event__shortName',
        'event__description',
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for event sponsors
class EventSponsorViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating event sponsors."""

    serializer_class = serializers.EventSponsorSerializer
    queryset = models.EventSponsor.objects.all()
    lookup_field = 'name'
    search_fields = (
        'name',
        'organisationId__name',
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for organisation
class OrganisationViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating organisations."""

    serializer_class = serializers.OrganisationSerializer
    queryset = models.Organisation.objects.all()
    lookup_field = 'name'
    search_fields = (
        'name',
        'description',
        'homepage',
        'orgid',
        'fields__field',
        'city',
    )
    filterset_fields = ('fields',)

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


class CertificationViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating organisations."""

    serializer_class = serializers.CertificationSerializer
    queryset = models.Certification.objects.all()
    # We can't use name if we want to keeep "CATI / CTAI" certification
    # lookup_field = 'name'
    search_fields = (
        'name',
        'description',
        'homepage',
    )


# Model ViewSet for elixirPlatform
class ElixirPlatformViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating elixirPlatforms."""

    serializer_class = serializers.ElixirPlatformSerializer
    queryset = models.ElixirPlatform.objects.all()
    lookup_field = 'name'
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
    filterset_fields = (
        'coordinator',
        'deputies',
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for elixirPlatform
class CommunityViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating elixirPlatforms."""

    serializer_class = serializers.CommunitySerializer
    queryset = models.Community.objects.all()
    lookup_field = 'name'
    search_fields = (
        'name',
        'description',
        'homepage',
        'organisations__name',
    )
    filterset_fields = ('organisations',)

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for projects
class ProjectViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating projects."""

    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all()
    lookup_field = 'name'
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
    filterset_fields = (
        'topics',
        'team',
        'hostedBy',
        'fundedBy',
        'communities',
        'elixirPlatforms',
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for resources
class ResourceViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating resources."""

    lookup_field = 'name'
    search_fields = (
        'name',
        'description',
        'communities__name',
        'elixirPlatforms__name',
    )
    filterset_fields = (
        'communities',
        'elixirPlatforms',
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for computing facilities
class ComputingFacilityViewSet(ResourceViewSet):
    """Handles creating, reading and updating computing facilities."""

    serializer_class = serializers.ComputingFacilitySerializer
    queryset = models.ComputingFacility.objects.all()
    search_fields = ResourceViewSet.search_fields + (
        'homepage',
        'providedBy__name',
        'accessibility',
    )
    filterset_fields = ResourceViewSet.filterset_fields + (
        'providedBy',
        'accessibility',
    )


# Model ViewSet for training materials
class TrainingMaterialViewSet(ResourceViewSet):
    """Handles creating, reading and updating training materials."""

    serializer_class = serializers.TrainingMaterialSerializer
    queryset = models.TrainingMaterial.objects.all()
    search_fields = ResourceViewSet.search_fields + (
        'doi__doi',
        'fileName',
        'topics__uri',
        'keywords__keyword',
        'audienceTypes__audienceType',
        'audienceRoles__audienceRole',
        'difficultyLevel',
        'providedBy__name',
    )
    filterset_fields = ResourceViewSet.filterset_fields + (
        'topics',
        'keywords',
        'audienceTypes',
        'audienceRoles',
        'difficultyLevel',
        'providedBy',
        'licence',
    )


class TeamFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Is active",
    )

    class Meta:
        model = models.Team
        fields = (
            'expertise',
            'leaders',
            'deputies',
            'scientificLeaders',
            'technicalLeaders',
            'members',
            'fields',
            'communities',
            'projects',
            'fundedBy',
            'keywords',
            'platforms',
            'ifbMembership',
            'is_active',
        )


# Model ViewSet for teams
class TeamViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating teams."""

    serializer_class = serializers.TeamSerializer
    queryset = models.Team.objects.all()
    lookup_field = 'name'
    search_fields_light = (
        'name',
        'description',
        'expertise__label',
        'leaders__firstname',
        'leaders__lastname',
        'keywords__keyword',
    )
    search_fields_all = search_fields_light + (
        'deputies__firstname',
        'deputies__lastname',
        'scientificLeaders__firstname',
        'scientificLeaders__lastname',
        'technicalLeaders__firstname',
        'technicalLeaders__lastname',
        # 'members__firstname', # take 9s more to answer, removing it
        # 'members__lastname',  # take 9s more to answer, removing it
        'certifications__name',
        'orgid',
        'unitId',
        'address',
        'city',
        'country',
        'fields__field',
        'communities__name',
        'projects__name',
        'fundedBy__name',
        # 'publications__doi', # take 3s more to answer, removing it
    )
    filterset_class = TeamFilter

    def get_queryset(self):
        return models.Team.annotate_is_active(super().get_queryset())

    @property
    def search_fields(self):
        if self.request.GET.get('wide', 'False') == 'True':
            return self.search_fields_all
        return self.search_fields_light

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


class ServiceCategoryViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.ServiceCategory.objects.all()
    serializer_class = misc.inline_serializer_factory(models.ServiceCategory, lookup_field='name')
    lookup_field = 'name'


class ServiceDomainViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.ServiceDomain.objects.all()
    serializer_class = misc.inline_serializer_factory(models.ServiceDomain, lookup_field='name')
    lookup_field = 'name'


class KindOfAnalysisViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.KindOfAnalysis.objects.all()
    serializer_class = misc.inline_serializer_factory(models.KindOfAnalysis, lookup_field='name')
    lookup_field = 'name'


class LifeScienceCommunityViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.LifeScienceCommunity.objects.all()
    serializer_class = misc.inline_serializer_factory(models.LifeScienceCommunity, lookup_field='name')
    lookup_field = 'name'


# Model ViewSet for services
class ServiceViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    serializer_class = serializers.ServiceSerializer
    queryset = models.Service.objects.all()
    search_fields = (
        'domain__name',
        'category__name',
        'team__name',
        'analysis__name',
        'communities__name',
        'comments',
    )
    filterset_fields = (
        'team',
        'analysis',
        'domain',
        'category',
    )


# # Model ViewSet for teams
# class BioinformaticsTeamViewSet(TeamViewSet):
#     """Handles creating, reading and updating bioinformatics teams."""
#
#     serializer_class = serializers.BioinformaticsTeamSerializer
#     queryset = models.BioinformaticsTeam.objects.all()
#     search_fields = TeamViewSet.search_fields + (
#         'edamTopics__uri',
#         'ifbMembership',
#         'platforms__name',
#     )
#     filterset_fields = TeamViewSet.search_fields + (
#         'edamTopics',
#         'ifbMembership',
#         'platforms',
#     )


# Model ViewSet for tools
class ToolViewSet(MultipleFieldLookupMixin, PermissionInClassModelViewSet, viewsets.ModelViewSet):
    pagination_class = pagination.LimitOffsetPagination
    """Handles creating, reading and updating tools."""

    serializer_class = serializers.ToolSerializer
    queryset = models.Tool.objects.all()
    lookup_fields = ['pk', 'biotoolsID__iexact']
    search_fields = (
        'name',
        'description',
        'tool_type__name',
    )
    filterset_fields = (
        'tool_type',
        'scientific_topics',
        'operating_system',
        'collection',
    )


class OperatingSystemChoicesViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.OperatingSystem.objects.all()
    serializer_class = serializers.modelserializer_factory(models.OperatingSystem, fields=['id', 'name'])
    lookup_field = 'name'


class ToolTypeViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.ToolType.objects.all()
    serializer_class = serializers.modelserializer_factory(models.ToolType, fields=['id', 'name'])


class TopicViewSet(MultipleFieldLookupMixin, PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.Topic.objects.all()
    serializer_class = serializers.modelserializer_factory(
        models.Topic,
        fields=[
            'id',
            'uri',
            'label',
            'synonyms',
            'description',
        ],
    )
    lookup_fields = ['pk', 'uri__endswith']
    search_fields = [
        'uri',
        'label',
        'synonyms',
        'description',
    ]


class EventCostViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.EventCost.objects.all()
    serializer_class = serializers.modelserializer_factory(models.EventCost, fields=['id', 'cost'])


class FieldViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.Field.objects.all()
    serializer_class = serializers.modelserializer_factory(models.Field, fields=['id', 'field'])


class AudienceTypeViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.AudienceType.objects.all()
    serializer_class = serializers.modelserializer_factory(models.AudienceType, fields=['id', 'audienceType'])


class AudienceRoleViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.AudienceRole.objects.all()
    serializer_class = serializers.modelserializer_factory(models.AudienceRole, fields=['id', 'audienceRole'])


class LicenceViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.Licence.objects.all()
    serializer_class = serializers.modelserializer_factory(models.Licence, fields=['id', 'name'])


@staff_member_required
def new_training_course(request, training_pk):
    training = get_object_or_404(models.Training, pk=training_pk)
    if not business_logic.has_view_permission(models.Training, request=request, obj=training):
        return HttpResponseForbidden('You cannot see this training.')
    if not business_logic.has_add_permission(models.Event, request=request):
        return HttpResponseForbidden('You cannot create new Event.')
    course, redirect_url = TrainingAdmin.create_new_course_and_get_admin_url(request=request, training=training)
    return HttpResponseRedirect(redirect_url)


@staff_member_required
def view_training_courses(request, training_pk):
    training = get_object_or_404(models.Training, pk=training_pk)
    if not business_logic.has_view_permission(models.Training, request=request, obj=training):
        return HttpResponseForbidden('You cannot see this training.')
    if not business_logic.has_view_permission(models.Event, request=request):
        return HttpResponseForbidden('You cannot see Event.')
    opts = models.Event._meta
    redirect_url = (
        reverse(
            'admin:%s_%s_changelist' % (opts.app_label, opts.model_name),
        )
        + f'?training__id__exact={training_pk}'
    )
    return HttpResponseRedirect(redirect_url)


@staff_member_required
def user_edition_history(request, user_id):
    object = get_object_or_404(get_user_model().objects, pk=user_id)
    # Adapted from django.contrib.admin.options.history_view
    from django.contrib.admin.models import LogEntry

    opts = get_user_model()._meta
    action_list = LogEntry.objects.filter(user_id=user_id).select_related().order_by('-action_time')

    print(get_permission_codename('change', opts))
    context = {
        'action_list': action_list,
        'module_name': str(capfirst(opts.verbose_name_plural)),
        'object': object,
        'opts': opts,
    }

    return render(
        request=request,
        template_name='admin/user_history.html',
        context=context,
    )


class MarkdownToHTMLJob(APIView):

    renderer_classes = [
        StaticHTMLRenderer,
    ]

    def post(self, request, format=None):
        serializer = serializers.MarkdownToHTMLSerializer(data=request.data, context={**request.data})
        if not serializer.is_valid():
            return Response(serializer.errors, status=rest_framework.status.HTTP_400_BAD_REQUEST)
        return Response(
            markdown(
                serializer.get_md(),
                extensions=['markdown.extensions.fenced_code'],
            )
        )


@staff_member_required
def update_from_biotools_view(request, pk):
    # Disclaimer : this view allows admin without permission to update a tool to trigger its update anyway
    opts = models.Tool._meta
    models.Tool.objects.get(pk=pk).update_information_from_biotool()
    return HttpResponseRedirect(reverse('admin:%s_%s_change' % (opts.app_label, opts.model_name), args=[pk]))


# @api_view(['POST'])
# @renderer_classes([StaticHTMLRenderer])
# @parser_classes([JSONParser])
# def md_to_html_view(request):
#     print(request.data)
#     serializer = serializers.MdToHTMLSerializer(data=request.data, context={**request.data})
#     if not serializer.is_valid():
#         return Response(serializer.errors, status=rest_framework.status.HTTP_400_BAD_REQUEST)
#     return Response(markdown(
#         serializer.data["md"],
#         extensions=['markdown.extensions.fenced_code'],
#     ))
