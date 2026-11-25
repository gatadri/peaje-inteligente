from drf_spectacular.extensions import OpenApiAuthenticationExtension


class PeajeJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "usuarios.authentication.PeajeJWTAuthentication"
    name = "jwtAuth"
    priority = 1

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }