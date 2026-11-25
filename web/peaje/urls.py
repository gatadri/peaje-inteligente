from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register(
    "vehiculos",
    views.VehiculoViewSet
)

router.register(
    "casetas",
    views.CasetaViewSet
)

router.register(
    "tarifas",
    views.TarifaViewSet
)

router.register(
    "pasos",
    views.PasoViewSet
)

router.register(
    "alertas",
    views.AlertaViewSet
)


urlpatterns = [

    path(
        "pasos/frame",
        views.procesar_frame
    ),

    path(
        "placas/consultar",
        views.consulta_placa_api
    ),

    path(
        "placas/consultar-imagen",
        views.consulta_imagen_api
    ),

    path(
        "placas/<str:placa>/historial",
        views.historial_placa
    ),

    path(
        "casetas/<int:id>/resumen",
        views.resumen_caseta
    ),

    path(
        "inferencia/estado",
        views.estado_api
    ),

    path(
        "alertas/<int:id>/atender",
        views.atender_alerta
    ),

    path("", include(router.urls)),
]