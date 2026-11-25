from django.db import models
from django.conf import settings


CATEGORIAS = [
    ("moto", "Motocicleta"),
    ("auto", "Automóvil"),
    ("minibus", "Minibús"),
    ("camion", "Camión"),
    ("bus", "Bus"),
]


class Vehiculo(models.Model):

    placa = models.CharField(
        max_length=15,
        unique=True
    )

    propietario = models.CharField(max_length=150)

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS
    )

    ejes = models.PositiveIntegerField(default=2)

    saldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "vehiculos"

    def __str__(self):
        return self.placa


class Caseta(models.Model):

    nombre = models.CharField(max_length=100)

    ubicacion = models.CharField(max_length=200)

    class Meta:
        db_table = "casetas"

    def __str__(self):
        return self.nombre


class Tarifa(models.Model):

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS
    )

    ejes = models.PositiveIntegerField()

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        db_table = "tarifas"

        constraints = [
            models.UniqueConstraint(
                fields=["categoria", "ejes"],
                name="tarifa_categoria_ejes"
            )
        ]

    def __str__(self):
        return (
            f"{self.categoria} - "
            f"{self.ejes} ejes - Bs. {self.monto}"
        )


class Paso(models.Model):

    ESTADOS = [
        ("aprobado", "Aprobado"),
        ("placa_desconocida", "Placa desconocida"),
        ("saldo_insuficiente", "Saldo insuficiente"),
        ("revision", "Revisión manual"),
    ]

    placa_leida = models.CharField(
        max_length=30,
        blank=True
    )

    placa_normalizada = models.CharField(
        max_length=15,
        blank=True,
        db_index=True
    )

    confianza_ocr = models.FloatField(default=0)

    categoria_detectada = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        blank=True,
        null=True
    )

    ejes_detectados = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    caseta = models.ForeignKey(
        Caseta,
        on_delete=models.PROTECT
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    imagen_url = models.ImageField(
        upload_to="evidencias/%Y/%m/%d/",
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="revision"
    )

    latencia_ms = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pasos"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.placa_normalizada} - "
            f"{self.estado}"
        )


class Alerta(models.Model):

    TIPOS = [
        ("placa_desconocida", "Placa desconocida"),
        ("saldo_insuficiente", "Saldo insuficiente"),
        ("revision", "Revisión manual"),
    ]

    paso = models.ForeignKey(
        Paso,
        on_delete=models.CASCADE,
        related_name="alertas"
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS
    )

    atendida = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alertas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tipo} - {self.paso}"