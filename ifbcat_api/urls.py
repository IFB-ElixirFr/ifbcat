# Imports
# ", include" imports the "include" function
# "DefaultRouter" is used to generate different routes (endpoints) for any ViewSets
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ifbcat_api import views

# A router is used to register required endpoints for API ViewSets
# e.g. "list" requests use the root of the API, whereas "update", "delete" etc. must access a specific object
# 'testviewset' is the URL we're regstering - the router will create URLs for us, so don't need to give a trailing '/'
# "base_name" is used if/wehn URLs are retrieved using URL-retrieving function provided by Django
# NB. don't need to specify base_name for userprofile (Model ViewSet) - it includes the queryset object (so Django can figure out the name)

router = DefaultRouter()
router.register('certification', views.CertificationViewSet)
router.register('community', views.CommunityViewSet)
router.register('computingfacility', views.ComputingFacilityViewSet)
router.register('elixirplatform', views.ElixirPlatformViewSet, basename='elixirplatform')
router.register('eventprerequisite', views.EventPrerequisiteViewSet)
router.register('eventsponsor', views.EventSponsorViewSet, basename='eventsponsor')
router.register('event', views.EventViewSet)
router.register('keyword', views.KeywordViewSet)
router.register('organisation', views.OrganisationViewSet, basename='organisation')
router.register('project', views.ProjectViewSet)
router.register('servicesubmission', views.ServiceSubmissionViewSet)
router.register('service', views.ServiceViewSet)
router.register('source_info', views.SourceInfoViewSet, basename='source_info')
router.register('team', views.TeamViewSet, basename='team')
router.register('team-cnp', views.TeamCNPViewSet, basename='team-cnp')
router.register('tool', views.ToolViewSet)
router.register('trainer', views.TrainerViewSet)
router.register('trainingeventmetrics', views.TrainingEventMetricsViewSet)
router.register('trainingevent', views.TrainingEventViewSet)
router.register('trainingmaterial', views.TrainingMaterialViewSet)
router.register('userprofile', views.UserProfileViewSet)

urlpatterns = [
    # path('testapiview/', views.TestApiView.as_view()),
    path('tool/<int:pk>/', views.ToolViewSet.as_view({'get': 'retrieve'})),
    path('tool/<biotoolsID>/', views.ToolViewSet.as_view({'get': 'retrieve'})),
    path('login/', views.UserLoginApiView.as_view()),
    path('', include(router.urls)),
]
