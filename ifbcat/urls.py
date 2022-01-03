"""ifbcat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Imports
# ' , include' is a functon used to include URLs from other apps (in this case from ifbcat_api)
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('', include('ifbcat_vanilla_front.urls')),
    path(
        'admin/password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='admin_password_reset',
    ),
    path(
        'admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
    path(
        'accounts/profile/',
        RedirectView.as_view(url='/admin/'),
    ),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('secureadmin/', admin.site.urls),
    path('api/', include('ifbcat_api.urls')),
    path('api/tess/', include('ifbcat_api.tess_urls')),
    path('', RedirectView.as_view(url='/team/', permanent=False)),
    path(
        'swagger-ui/',
        TemplateView.as_view(template_name='swagger-ui.html', extra_context={'schema_url': 'openapi-schema'}),
        name='swagger-ui',
    ),
    path(
        'openapi',
        get_schema_view(
            title="IFB Catalog",
            description="A catalog of bioinformatics resources such as software, database, organisation, training, ...",
            version="1.0.0b",
        ),
        name='openapi-schema',
    ),
]
