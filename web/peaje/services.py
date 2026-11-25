import re

from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import Vehiculo, Paso, Tarifa, Alerta


def normalizar_placa(placa):

    return re.sub(
        r"[^A-Z0-9]",
        "",
        str(placa or "").upper()
    )


def placa_valida(placa):

    return bool(
        re.fullmatch(
            r"\d{3,4}[A-Z]{3}",
            placa
        )
    )


@transaction.atomic
def registrar_paso(resultado, imagen, caseta, usuario):

    placa = normalizar_placa(
        resultado.get("placa")
    )

    categoria = resultado.get("categoria")

    ejes = resultado.get("ejes")

    confianza = float(
        resultado.get("confianza_ocr") or 0
    )

    monto = Decimal("0.00")

    estado = "revision"

    vehiculo = Vehiculo.objects.select_for_update().filter(
        placa=placa,
        activo=True
    ).first()

    # Evitar cobros repetidos por fotogramas consecutivos

    if placa_valida(placa):

        anterior = Paso.objects.filter(
            placa_normalizada=placa,
            caseta=caseta,
            estado="aprobado",
            created_at__gte=(
                timezone.now()
                - timezone.timedelta(seconds=60)
            )
        ).first()

        if anterior:

            return anterior

    # Validar placa y datos detectados

    if not placa_valida(placa) or confianza < 0.5:

        estado = "revision"

    elif vehiculo is None:

        estado = "placa_desconocida"

    elif not categoria or not ejes:

        estado = "revision"

    elif (
        categoria != vehiculo.categoria
        or ejes != vehiculo.ejes
    ):

        estado = "revision"

    else:

        tarifa = Tarifa.objects.filter(
            categoria=categoria,
            ejes=ejes
        ).first()

        if tarifa is None:

            estado = "revision"

        elif vehiculo.saldo < tarifa.monto:

            estado = "saldo_insuficiente"

        else:

            monto = tarifa.monto

            vehiculo.saldo -= monto

            vehiculo.save(
                update_fields=["saldo"]
            )

            estado = "aprobado"

    paso = Paso.objects.create(
        placa_leida=resultado.get("placa") or "",
        placa_normalizada=placa,
        confianza_ocr=confianza,
        categoria_detectada=categoria,
        ejes_detectados=ejes,
        monto=monto,
        caseta=caseta,
        usuario=usuario,
        imagen_url=imagen,
        estado=estado,
        latencia_ms=resultado.get("latencia_ms") or 0
    )

    if estado != "aprobado":

        Alerta.objects.create(
            paso=paso,
            tipo=estado
        )

    return paso


def consultar_placa(placa):

    placa = normalizar_placa(placa)

    if not placa_valida(placa):

        return {
            "estado": "formato_invalido",
            "placa": placa,
            "mensaje": "La placa no tiene un formato válido."
        }

    vehiculo = Vehiculo.objects.filter(
        placa=placa,
        activo=True
    ).first()

    pasos = Paso.objects.filter(
        placa_normalizada=placa
    )

    ultimo = pasos.first()

    if vehiculo and ultimo:

        return {
            "estado": "registrado_con_pasos",
            "placa": placa,
            "propietario": vehiculo.propietario,
            "categoria": vehiculo.categoria,
            "saldo": float(vehiculo.saldo),
            "total_pasos": pasos.count(),
            "ultimo_paso": {
                "fecha": ultimo.created_at.isoformat(),
                "caseta": ultimo.caseta.nombre,
                "categoria": ultimo.categoria_detectada,
                "monto": float(ultimo.monto),
                "estado": ultimo.estado
            }
        }

    if vehiculo:

        return {
            "estado": "registrado_sin_pasos",
            "placa": placa,
            "propietario": vehiculo.propietario,
            "categoria": vehiculo.categoria,
            "saldo": float(vehiculo.saldo),
            "mensaje": "Vehículo registrado sin pasos."
        }

    if ultimo:

        return {
            "estado": "identificado_no_registrado",
            "placa": placa,
            "total_pasos": pasos.count(),
            "mensaje": "Vehículo detectado pero no registrado."
        }

    return {
        "estado": "inexistente",
        "placa": placa,
        "mensaje": "No existen registros de esta placa."
    }