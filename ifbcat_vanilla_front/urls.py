from django.conf.urls import url

from ifbcat_vanilla_front import views

app_name = 'vfront'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^platform/$', views.TeamListView.as_view(), name='team-list'),
    url(r'^platform/(?P<slug>[-\w ]+)/$', views.TeamDetailView.as_view(), name='team-detail'),
    url(r'^event/$', views.EventListView.as_view(), name='event-list'),
    url(r'^event/(?P<pk>\d+)/$', views.EventDetailView.as_view(), name='event-detail'),
    url(r'^training/$', views.TrainingListView.as_view(), name='training-list'),
    url(r'^training/(?P<pk>\d+)/$', views.TrainingDetailView.as_view(), name='training-detail'),
]
