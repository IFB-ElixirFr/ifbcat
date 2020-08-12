# Imports
# ", include" imports the "include" function
# "DefaultRouter" is used to generate different routes (endpoints) for any ViewSets
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ifbcatsandbox_api import views

# A router is used to register required endpoints for API ViewSets
# e.g. "list" requests use the root of the API, whereas "update", "delete" etc. must access a specific object
# 'testviewset' is the URL we're regstering - the router will create URLs for us, so don't need to give a trailing '/'
# "base_name" is used if/wehn URLs are retrieved using URL-retrieving function provided by Django
# NB. don't need to specify base_name for userprofile (Model ViewSet) - it includes the queryset object (so Django can figure out the name)
router = DefaultRouter()
router.register('testviewset', views.TestViewSet, basename='testviewset')
router.register('userprofile', views.UserProfileViewSet)
router.register('news', views.NewsItemViewSet)
router.register('event', views.EventViewSet)
router.register('eventkeyword', views.EventKeywordViewSet)
router.register('eventprerequisite', views.EventPrerequisiteViewSet)
router.register('organisation', views.OrganisationViewSet)
router.register('elixirplatform', views.ElixirPlatformViewSet)
router.register('community', views.CommunityViewSet)
router.register('project', views.ProjectViewSet)
router.register('computingfacility', views.ComputingFacilityViewSet)
router.register('trainer', views.TrainerViewSet)
router.register('trainingeventmetrics', views.TrainingEventMetricsViewSet)
router.register('eventsponsor', views.EventSponsorViewSet)

# APIView ("testapiview" below) endpoints are registered differently than API ViewSet
# "include" function is used to include a list of URLS into the URL pattern
# It figures out the URLs for all the functions ("list" etc.) defined in views.py for the ViewSet - hence the blank string as 1st arg.
urlpatterns = [
    # path('testapiview/', views.TestApiView.as_view()),
    path('login/', views.UserLoginApiView.as_view()),
    path('', include(router.urls)),
]
