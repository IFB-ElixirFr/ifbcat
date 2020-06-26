from django.urls import path
from ifbcatsandbox_api import views

urlpatterns = [
path('changelog/', views.ChangelogView.as_view()),
]
