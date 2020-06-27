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
router.register('testviewset', views.TestViewSet, base_name='testviewset')
router.register('userprofile', views.UserProfileViewSet)

# APIView ("changelog" below) endpoints are registered differently than API ViewSet
# "include" function is used to include a list of URLS into the URL pattern
# It figures out the URLs for all the functions ("list" etc.) defined in views.py for the ViewSet - hence the blank string as 1st arg.
urlpatterns = [
path('changelog/', views.ChangelogView.as_view()),
path('', include(router.urls))
]
