import re

from rest_framework.decorators import api_view
from rest_framework.response import Response

from peaje.services import consultar_placa
from peaje.inferencia import consultar_inferencia


@api_view(["POST"])
def chat(request):

    mensaje = str(
        request.data.get("mensaje", "")
    ).upper()

    imagen = request.FILES.get("imagen")

    if imagen:

        try:
            resultado = consultar_inferencia(
                imagen, "ocr"
            )

            placa = resultado.get("placa")

            if (
                not placa
                or not resultado.get("formato_valido")
                or float(resultado.get("confianza") or 0) < 0.5
            ):
                return Response({
                    "respuesta": "No pude leer la placa. Envíame una imagen más clara."
                })

        except Exception:

            return Response({
                "respuesta": "El servicio OCR no está disponible."
            }, status=503)

    else:

        coincidencia = re.search(
            r"\b(\d{3,4})[\s-]*([A-Z]{3})\b",
            mensaje
        )

        if not coincidencia:

            return Response({
                "respuesta": "Escribe una placa válida, por ejemplo 1234ABC, o envía una fotografía."
            })

        placa = (
            coincidencia.group(1)
            + coincidencia.group(2)
        )

    datos = consultar_placa(placa)

    estado = datos["estado"]

    if estado == "registrado_con_pasos":

        paso = datos["ultimo_paso"]

        respuesta = (
            f"El vehículo {placa} está registrado. "
            f"Propietario: {datos['propietario']}. "
            f"Último paso: {paso['fecha']}. "
            f"Caseta: {paso['caseta']}. "
            f"Categoría: {paso['categoria']}. "
            f"Monto: Bs {paso['monto']}. "
            f"Estado: {paso['estado']}."
        )

    elif estado == "registrado_sin_pasos":

        respuesta = (
            f"El vehículo {placa} está registrado, "
            f"pero todavía no tiene pasos. "
            f"Categoría: {datos['categoria']}. "
            f"Saldo: Bs {datos['saldo']}."
        )

    elif estado == "identificado_no_registrado":

        respuesta = (
            f"La placa {placa} fue identificada "
            "en el sistema de peaje, pero el "
            "vehículo no está registrado."
        )

    elif estado == "inexistente":

        respuesta = (
            f"No existen registros de la placa {placa}."
        )

    else:

        respuesta = datos.get(
            "mensaje", "Placa inválida."
        )

    return Response({
        "respuesta": respuesta,
        "datos": datos
    })