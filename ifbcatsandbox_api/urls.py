from django.urls import path
from ifbcatsandbox_api import views

urlpatterns = [
path('status/', views.StatusView.as_view()),
]
