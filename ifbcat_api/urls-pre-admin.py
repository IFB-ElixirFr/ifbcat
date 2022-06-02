from django.urls import path

from ifbcat_api import views

urlpatterns = [
    path(
        'ifbcat_api/userprofile/<int:user_id>/edition-history/',
        views.user_edition_history,
        name='user_edition_history',
    ),
]
