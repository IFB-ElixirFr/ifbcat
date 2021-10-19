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

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models import When, Q, Case, Value, CharField, Min, Max
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters import rest_framework as django_filters
from rest_framework import pagination
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from ifbcat_api import models, business_logic
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

    @method_decorator(cache_page(int(60 * 60 * 0.5)))
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
        'teamLeader',
        'teamsMembers',
        'elixirPlatformDeputies',
        'elixirPlatformCoordinator',
    )

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.UserProfileSerializerTiny
        return serializers.UserProfileSerializer


# Class for handling user authentication.
# ObtainAuthToken has to be customised so that is enabled in the Django admin site
# (this is not not enabled by default)
class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication tokens."""

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class EventFilter(AutoSubsetFilterSet):
    min_start = django_filters.DateFilter(field_name="dates__dateStart", lookup_expr='gte')
    max_start = django_filters.DateFilter(field_name="dates__dateStart", lookup_expr='lte')
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
            'contactId',
            'elixirPlatforms',
            'communities',
            'organisedByTeams',
            'organisedByOrganisations',
            'sponsoredBy',
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
            'contactId',
            'elixirPlatforms',
            'communities',
            'organisedByTeams',
            'organisedByOrganisations',
            'sponsoredBy',
            'computingFacilities',
        ]


# Model ViewSet for events
class EventViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating events."""

    serializer_class = serializers.EventSerializer
    ordering = ['-dates']
    queryset = (
        models.Event.objects.annotate(
            dateStartMin=Min('dates__dateStart'),
            dateEndMin=Max('dates__dateEnd'),
        )
        .annotate(
            realisation_status=Case(
                When(Q(dateStartMin__gt=timezone.now()), then=Value('future')),
                When(
                    Q(dateStartMin__lt=timezone.now())
                    & (Q(dateEndMin__isnull=True) | Q(dateEndMin__lt=timezone.now())),
                    then=Value('past'),
                ),
                default=Value('ongoing'),
                output_field=CharField(),
            )
        )
        .annotate(
            registration_status=Case(
                When(
                    Q(registration_opening__gt=timezone.now()),
                    then=Value('future'),
                ),
                When(
                    (Q(registration_opening__isnull=False) | Q(registration_closing__isnull=False))
                    & (Q(registration_opening__isnull=True) | Q(registration_opening__lt=timezone.now()))
                    & (Q(registration_closing__isnull=True) | Q(registration_closing__gt=timezone.now())),
                    then=Value('open'),
                ),
                When(
                    Q(registration_opening__isnull=True) & Q(registration_closing__isnull=True),
                    then=Value('unknown'),
                ),
                default=Value('closed'),
                output_field=CharField(),
            )
        )
    )
    search_fields_from_abstract_event = (
        'name',
        'shortName',
        'description',
        'costs__cost',
        'topics__uri',
        'keywords__keyword',
        'prerequisites__prerequisite',
        'accessibility',
        'accessibilityNote',
        'contactName',
        'contactId__email',
        'contactEmail',
        'elixirPlatforms__name',
        'communities__name',
        'organisedByTeams__name',
        'organisedByOrganisations__name',
        'sponsoredBy__name',
        'sponsoredBy__organisationId__name',
    )
    search_fields = search_fields_from_abstract_event + (
        'type',
        'venue',
        'city',
        'country',
        'trainers__trainerName',
        'trainers__trainerId__email',
    )
    filterset_class = EventFilter

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


# Model ViewSet for training events that should be published in TES
class TessEventViewSet(EventViewSet):
    queryset = models.Event.annotate_is_tess_publishing().filter(is_tess_publishing=True)


# Model ViewSet for training
class TrainingViewSet(EventViewSet):
    """Handles creating, reading and updating training events."""

    serializer_class = serializers.TrainingSerializer
    ordering = []
    queryset = models.Training.objects.all()

    search_fields = EventViewSet.search_fields_from_abstract_event + (
        'audienceTypes__audienceType',
        'audienceRoles__audienceRole',
        'difficultyLevel',
        'learningOutcomes',
    )
    filterset_class = TrainingFilter


# Model ViewSet for training that should be published in TES
class TessTrainingViewSet(TrainingViewSet):
    queryset = models.Training.objects.filter(tess_publishing=True)


# Model ViewSet for keywords
class KeywordViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating keywords."""

    serializer_class = serializers.KeywordSerializer
    queryset = models.Keyword.objects.all()
    # lookup_field = 'keyword__unaccent__iexact'
    search_fields = ('keyword',)

    def perform_create(self, serializer):
        """Saves the serializer."""
        serializer.save()


# Model ViewSet for event prerequisites
class EventPrerequisiteViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating event prerequisites."""

    serializer_class = serializers.EventPrerequisiteSerializer
    queryset = models.EventPrerequisite.objects.all()
    search_fields = ('prerequisite',)

    def perform_create(self, serializer):
        """Saves the serializer."""
        serializer.save()


# Model ViewSet for trainer
class TrainerViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating trainers."""

    serializer_class = serializers.TrainerSerializer
    queryset = models.Trainer.objects.all()
    search_fields = (
        'trainerName',
        'trainerEmail',
        'trainerId__email',
        'trainerId__firstname',
        'trainerId__lastname',
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


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
        'license',
    )
    filterset_fields = ResourceViewSet.filterset_fields + (
        'topics',
        'keywords',
        'audienceTypes',
        'audienceRoles',
        'difficultyLevel',
        'providedBy',
        'license',
    )


# Model ViewSet for teams
class TeamViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating teams."""

    serializer_class = serializers.TeamSerializer
    queryset = models.Team.objects.all()
    lookup_field = 'name'
    # TODO: : add to "search_fields" below:   'team', 'providedBy'
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
        'certifications__name',
        'orgid',
        'unitId',
        'address',
        'fields__field',
        'communities__name',
        'projects__name',
        'fundedBy__name',
        'publications__doi',
        'keywords__keyword',
    )
    filterset_fields = (
        'expertise',
        'leader',
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
    )

    def perform_create(self, serializer):
        """Sets the user profile to the logged-in user."""
        serializer.save(user_profile=self.request.user)


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


# Model ViewSet for services
class ServiceViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating services."""

    serializer_class = serializers.ServiceSerializer
    queryset = models.Service.objects.all()
    lookup_field = 'name'
    # TODO: : add to "search_fields" below:   'team', 'providedBy'
    search_fields = (
        'name',
        'description',
        'computingFacilities__name',
        'teams__name',
        'trainings__name',
        'trainingMaterials__name',
        'publications__doi',
    )
    filterset_fields = (
        'teams',
        'computingFacilities',
    )


# Model ViewSet for service submissions
class ServiceSubmissionViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    """Handles creating, reading and updating service submissions."""

    serializer_class = serializers.ServiceSubmissionSerializer
    queryset = models.ServiceSubmission.objects.all()
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
    filterset_fields = (
        'service',
        'year',
    )


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
        'keywords',
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


class TopicViewSet(PermissionInClassModelViewSet, viewsets.ModelViewSet):
    queryset = models.Topic.objects.all()
    serializer_class = serializers.modelserializer_factory(models.Topic, fields=['id', 'uri', 'label'])


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
