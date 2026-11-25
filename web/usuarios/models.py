from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):

    ROLES = [
        ("admin", "Administrador"),
        ("operador", "Operador"),
    ]

    email_google = models.EmailField(unique=True)

    nombre = models.CharField(max_length=150)

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default="operador"
    )

    activo = models.BooleanField(default=True)

    REQUIRED_FIELDS = [
        "email_google",
        "nombre"
    ]

    class Meta:
        db_table = "usuarios"

    def __str__(self):
        return f"{self.nombre} - {self.rol}"