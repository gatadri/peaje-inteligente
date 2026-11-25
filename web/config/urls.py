from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

from peaje.dashboard import dashboard, eventos


urlpatterns = [

    path("", dashboard, name="dashboard"),

    path("eventos/", eventos),

    path(
        "admin/login/",
        lambda request: redirect("login")
    ),

    path("admin/", admin.site.urls),

    path("", include("usuarios.urls")),

    path(
        "api/v1/",
        include("peaje.urls")
    ),

    path(
        "api/v1/agente/",
        include("agente.urls")
    ),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema"
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger"
    ),
]

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )