from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    list_display = (
        "username",
        "email_google",
        "nombre",
        "rol",
        "activo",
    )

    list_filter = (
        "rol",
        "activo",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Sistema de peaje",
            {
                "fields": (
                    "email_google",
                    "nombre",
                    "rol",
                    "activo",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Sistema de peaje",
            {
                "fields": (
                    "email_google",
                    "nombre",
                    "rol",
                    "activo",
                )
            },
        ),
    )