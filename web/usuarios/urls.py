from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views


urlpatterns = [

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "auth/google/",
        views.google_login,
        name="google_login"
    ),

    path(
        "auth/google/callback/",
        views.google_callback,
        name="google_callback"
    ),

    path(
        "logout/",
        views.cerrar_sesion,
        name="logout"
    ),

    path(
        "api/v1/auth/google",
        views.google_api,
        name="google_api"
    ),

    path(
        "api/v1/auth/refresh",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
]