from rest_framework import serializers

from .models import (
    Vehiculo,
    Caseta,
    Tarifa,
    Paso,
    Alerta
)


class VehiculoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehiculo
        fields = "__all__"


class CasetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Caseta
        fields = "__all__"


class TarifaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tarifa
        fields = "__all__"


class PasoSerializer(serializers.ModelSerializer):

    nombre_caseta = serializers.CharField(
        source="caseta.nombre",
        read_only=True
    )

    nombre_usuario = serializers.CharField(
        source="usuario.nombre",
        read_only=True
    )

    class Meta:
        model = Paso
        fields = "__all__"


class AlertaSerializer(serializers.ModelSerializer):

    placa = serializers.CharField(
        source="paso.placa_normalizada",
        read_only=True
    )

    class Meta:
        model = Alerta
        fields = "__all__"


class FrameSerializer(serializers.Serializer):

    imagen = serializers.ImageField()

    caseta_id = serializers.IntegerField()


class ConsultaPlacaSerializer(serializers.Serializer):

    placa = serializers.CharField(max_length=30)


class ConsultaImagenSerializer(serializers.Serializer):

    imagen = serializers.ImageField()