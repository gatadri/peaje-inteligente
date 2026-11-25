import requests
from django.conf import settings


def consultar_inferencia(imagen, endpoint="predict"):

    url = (
        settings.INFERENCE_URL.rstrip("/")
        + "/" + endpoint
    )

    imagen.seek(0)

    respuesta = requests.post(
        url,
        files={
            "file": (
                imagen.name,
                imagen.read(),
                imagen.content_type
            )
        },
        headers={
            "Authorization": f"Bearer {settings.INFERENCE_TOKEN}",
            "ngrok-skip-browser-warning": "true"
        },
        timeout=120
    )

    imagen.seek(0)

    respuesta.raise_for_status()

    return respuesta.json()


def estado_inferencia():

    try:

        respuesta = requests.get(
            settings.INFERENCE_URL.rstrip("/") + "/health",
            headers={
                "ngrok-skip-browser-warning": "true"
            },
            timeout=10
        )

        respuesta.raise_for_status()

        return respuesta.json()

    except requests.RequestException:

        return {
            "estado": "offline"
        }