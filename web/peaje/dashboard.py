import json
import time

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.db.models import Sum
from django.db import close_old_connections
from django.utils import timezone

from .models import Paso, Alerta, Vehiculo, Caseta
from .serializers import PasoSerializer, AlertaSerializer


@login_required
def dashboard(request):

    return render(
        request,
        "peaje/dashboard.html",
        {
            "casetas": Caseta.objects.all()
        }
    )


def obtener_estadisticas():

    pasos = Paso.objects.filter(
        created_at__date=timezone.localdate()
    )

    return {
        "total": pasos.count(),
        "aprobados": pasos.filter(
            estado="aprobado"
        ).count(),
        "recaudacion": float(
            pasos.filter(
                estado="aprobado"
            ).aggregate(
                total=Sum("monto")
            )["total"] or 0
        ),
        "alertas": Alerta.objects.filter(
            atendida=False
        ).count(),
        "vehiculos": Vehiculo.objects.count(),
        "pasos": PasoSerializer(
            Paso.objects.all()[:30],
            many=True
        ).data,
        "lista_alertas": AlertaSerializer(
            Alerta.objects.all()[:30],
            many=True
        ).data
    }


@login_required
def eventos(request):

    usuario_id = request.user.pk

    def generar():

        from usuarios.models import Usuario

        anterior = None

        while True:

            close_old_connections()

            autorizado = Usuario.objects.filter(
                pk=usuario_id,
                activo=True,
                is_active=True
            ).exists()

            if not autorizado:
                break

            datos = json.dumps(
                obtener_estadisticas(),
                default=str
            )

            if datos != anterior:

                yield f"data: {datos}\n\n"

                anterior = datos

            else:

                yield ": heartbeat\n\n"

            close_old_connections()

            time.sleep(3)

    respuesta = StreamingHttpResponse(
        generar(),
        content_type="text/event-stream"
    )

    respuesta["Cache-Control"] = "no-cache"
    respuesta["X-Accel-Buffering"] = "no"

    return respuesta