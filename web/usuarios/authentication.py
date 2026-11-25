from rest_framework_simplejwt.authentication import (
    JWTAuthentication
)

from rest_framework.exceptions import AuthenticationFailed


class PeajeJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):

        usuario = super().get_user(validated_token)

        if not usuario.activo or not usuario.is_active:

            raise AuthenticationFailed(
                "Usuario desactivado o no autorizado"
            )

        return usuario