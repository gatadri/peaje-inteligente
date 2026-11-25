import requests

from django.db.models import Sum
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    Vehiculo,
    Caseta,
    Tarifa,
    Paso,
    Alerta
)

from .serializers import (
    VehiculoSerializer,
    CasetaSerializer,
    TarifaSerializer,
    PasoSerializer,
    AlertaSerializer,
    FrameSerializer,
    ConsultaPlacaSerializer,
    ConsultaImagenSerializer
)

from .permissions import EsAdministradorOLectura

from .inferencia import (
    consultar_inferencia,
    estado_inferencia
)

from .services import (
    registrar_paso,
    consultar_placa,
    normalizar_placa
)


class VehiculoViewSet(viewsets.ModelViewSet):

    queryset = Vehiculo.objects.all()

    serializer_class = VehiculoSerializer

    permission_classes = [
        EsAdministradorOLectura
    ]


class CasetaViewSet(viewsets.ModelViewSet):

    queryset = Caseta.objects.all()

    serializer_class = CasetaSerializer

    permission_classes = [
        EsAdministradorOLectura
    ]


class TarifaViewSet(viewsets.ModelViewSet):

    queryset = Tarifa.objects.all()

    serializer_class = TarifaSerializer

    permission_classes = [
        EsAdministradorOLectura
    ]


class PasoViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Paso.objects.all()

    serializer_class = PasoSerializer


class AlertaViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Alerta.objects.all()

    serializer_class = AlertaSerializer


@extend_schema(
    request=FrameSerializer,
    responses=PasoSerializer
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def procesar_frame(request):

    serializer = FrameSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    imagen = serializer.validated_data["imagen"]

    caseta_id = serializer.validated_data["caseta_id"]

    caseta = Caseta.objects.filter(
        id=caseta_id
    ).first()

    if caseta is None:

        return Response(
            {"error": "Caseta inexistente"},
            status=404
        )

    try:

        resultado = consultar_inferencia(
            imagen,
            "predict"
        )

    except requests.RequestException:

        return Response(
            {"error": "API de inferencia no disponible"},
            status=503
        )

    paso = registrar_paso(
        resultado,
        imagen,
        caseta,
        request.user
    )

    return Response(
        PasoSerializer(
            paso,
            context={"request": request}
        ).data
    )


@api_view(["POST"])
def consulta_placa_api(request):

    serializer = ConsultaPlacaSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    resultado = consultar_placa(
        serializer.validated_data["placa"]
    )

    return Response(resultado)


@api_view(["POST"])
def consulta_imagen_api(request):

    serializer = ConsultaImagenSerializer(
        data=request.data
    )

    serializer.is_valid(raise_exception=True)

    try:

        resultado = consultar_inferencia(
            serializer.validated_data["imagen"],
            "ocr"
        )

    except requests.RequestException:

        return Response(
            {"error": "API de inferencia no disponible"},
            status=503
        )

    placa = resultado.get("placa")

    if (
        not placa
        or not resultado.get("formato_valido")
        or float(resultado.get("confianza") or 0) < 0.5
    ):

        return Response({
            "estado": "imagen_ilegible",
            "mensaje": "No se pudo leer la placa. Envía otra imagen."
        })

    consulta = consultar_placa(placa)

    consulta["confianza_ocr"] = resultado.get(
        "confianza"
    )

    return Response(consulta)


@api_view(["GET"])
def historial_placa(request, placa):

    placa = normalizar_placa(placa)

    pasos = Paso.objects.filter(
        placa_normalizada=placa
    )

    return Response(
        PasoSerializer(
            pasos,
            many=True,
            context={"request": request}
        ).data
    )


@api_view(["GET"])
def resumen_caseta(request, id):

    caseta = Caseta.objects.filter(
        pk=id
    ).first()

    if not caseta:

        return Response(
            {"error": "Caseta inexistente"},
            status=404
        )

    pasos = Paso.objects.filter(
        caseta=caseta,
        created_at__date=timezone.localdate()
    )

    return Response({
        "caseta": caseta.nombre,
        "total_pasos": pasos.count(),
        "aprobados": pasos.filter(
            estado="aprobado"
        ).count(),
        "recaudacion": pasos.filter(
            estado="aprobado"
        ).aggregate(
            total=Sum("monto")
        )["total"] or 0,
        "alertas": Alerta.objects.filter(
            paso__in=pasos,
            atendida=False
        ).count()
    })


@api_view(["GET"])
def estado_api(request):

    return Response(
        estado_inferencia()
    )


@api_view(["POST"])
def atender_alerta(request, id):

    if request.user.rol != "admin":

        return Response(
            {"error": "Permisos insuficientes"},
            status=403
        )

    alerta = Alerta.objects.filter(
        id=id
    ).first()

    if not alerta:

        return Response(
            {"error": "Alerta inexistente"},
            status=404
        )

    alerta.atendida = True

    alerta.save(
        update_fields=["atendida"]
    )

    return Response({
        "mensaje": "Alerta atendida"
    })