import secrets
import requests

from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse
from django.views.decorators.http import require_POST

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario


def verificar_google(token):

    datos = id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        settings.GOOGLE_CLIENT_ID
    )

    if not datos.get("email_verified"):
        raise ValueError("Correo no verificado")

    correo = datos["email"].strip().lower()

    usuario = Usuario.objects.filter(
        email_google__iexact=correo,
        activo=True,
        is_active=True
    ).first()

    if usuario is None:
        raise PermissionError("Usuario no autorizado")

    return usuario


def login_view(request):

    if request.user.is_authenticated:
        return redirect("/")

    return render(
        request,
        "usuarios/login.html"
    )


def google_login(request):

    estado = secrets.token_urlsafe(32)

    request.session["oauth_state"] = estado

    callback = request.build_absolute_uri(
        reverse("google_callback")
    )

    parametros = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": callback,
        "response_type": "code",
        "scope": "openid email profile",
        "state": estado,
        "prompt": "select_account"
    }

    url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(parametros)
    )

    return redirect(url)


def google_callback(request):

    estado = request.GET.get("state")

    estado_guardado = request.session.pop(
        "oauth_state", None
    )

    if not estado or estado != estado_guardado:

        return render(
            request,
            "usuarios/login.html",
            {"error": "Solicitud de acceso inválida"},
            status=400
        )

    codigo = request.GET.get("code")

    if not codigo:

        return render(
            request,
            "usuarios/login.html",
            {"error": "Inicio de sesión cancelado"}
        )

    callback = request.build_absolute_uri(
        reverse("google_callback")
    )

    try:

        respuesta = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": codigo,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": callback,
                "grant_type": "authorization_code"
            },
            timeout=20
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        usuario = verificar_google(
            datos["id_token"]
        )

        login(
            request,
            usuario,
            backend="django.contrib.auth.backends.ModelBackend"
        )

        return redirect("/")

    except PermissionError:

        return render(
            request,
            "usuarios/login.html",
            {
                "error": (
                    "Acceso denegado. "
                    "Tu correo no está autorizado."
                )
            },
            status=403
        )

    except Exception:

        return render(
            request,
            "usuarios/login.html",
            {
                "error": (
                    "No se pudo verificar la cuenta de Google."
                )
            },
            status=400
        )


@require_POST
def cerrar_sesion(request):

    logout(request)

    return redirect("/login/")


@api_view(["POST"])
@permission_classes([AllowAny])
def google_api(request):

    token = request.data.get("id_token")

    if not token:

        return Response(
            {"error": "Se requiere id_token"},
            status=400
        )

    try:

        usuario = verificar_google(token)

        refresh = RefreshToken.for_user(usuario)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email_google,
                "rol": usuario.rol
            }
        })

    except PermissionError:

        return Response(
            {"error": "Usuario no autorizado"},
            status=403
        )

    except Exception:

        return Response(
            {"error": "Token de Google inválido"},
            status=401
        )