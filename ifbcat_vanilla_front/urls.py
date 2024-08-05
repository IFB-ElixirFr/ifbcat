from django.urls import path, re_path

from ifbcat_vanilla_front import views

app_name = 'vfront'
urlpatterns = [
    path('', views.index, name='home'),
    path('platform/', views.TeamListView.as_view(), name='team-list'),
    re_path(r'^platform/(?P<slug>[-\w ]+)/$', views.TeamDetailView.as_view(), name='team-detail'),
    path('event/', views.EventListView.as_view(), name='event-list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('training/', views.TrainingListView.as_view(), name='training-list'),
    path('training/<int:pk>/', views.TrainingDetailView.as_view(), name='training-detail'),
]
