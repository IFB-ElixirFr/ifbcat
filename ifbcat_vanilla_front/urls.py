from django.conf.urls import url

from ifbcat_vanilla_front import views

app_name = 'vfront'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^team/$', views.TeamListView.as_view(), name='team-list'),
    url(r'^team/(?P<slug>[-\w ]+)/$', views.TeamDetailView.as_view(), name='team-detail'),
]
