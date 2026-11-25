from django.contrib import admin

from .models import (
    Vehiculo,
    Caseta,
    Tarifa,
    Paso,
    Alerta
)


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):

    list_display = (
        "placa",
        "propietario",
        "categoria",
        "ejes",
        "saldo",
        "activo"
    )

    search_fields = (
        "placa",
        "propietario"
    )

    list_filter = (
        "categoria",
        "activo"
    )


@admin.register(Caseta)
class CasetaAdmin(admin.ModelAdmin):

    list_display = (
        "nombre",
        "ubicacion"
    )


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):

    list_display = (
        "categoria",
        "ejes",
        "monto"
    )


@admin.register(Paso)
class PasoAdmin(admin.ModelAdmin):

    list_display = (
        "placa_normalizada",
        "categoria_detectada",
        "ejes_detectados",
        "monto",
        "estado",
        "caseta",
        "created_at"
    )

    search_fields = (
        "placa_normalizada",
    )

    list_filter = (
        "estado",
        "categoria_detectada",
        "caseta"
    )


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):

    list_display = (
        "paso",
        "tipo",
        "atendida",
        "created_at"
    )

    list_filter = (
        "tipo",
        "atendida"
    )