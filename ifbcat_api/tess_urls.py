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
from ifbcat_api.views import CachedNoPaginationFactory

router_tess = DefaultRouter()
router_tess.register('event', CachedNoPaginationFactory(views.TessEventViewSet), basename='tess-event')
router_tess.register('training', CachedNoPaginationFactory(views.TessTrainingViewSet), basename='tess-training')

urlpatterns = [
    path('', include(router_tess.urls)),
]
