import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from decimal import Decimal
from usuarios.models import Usuario
from peaje.models import Vehiculo, Caseta, Tarifa


# DOCENTE AUTORIZADO

docente, creado = Usuario.objects.get_or_create(
    email_google="doc.alvaro.pinto.ma@unifranz.edu.bo",
    defaults={
        "username": "docente",
        "nombre": "Álvaro Pinto",
        "rol": "admin",
        "activo": True,
        "is_active": True,
        "is_staff": True,
        "is_superuser": True
    }
)

if creado:
    docente.set_unusable_password()
    docente.save()

# SEGUNDO ADMINISTRADOR

administradora, creado = Usuario.objects.update_or_create(
    email_google="ayllon814@gmail.com",
    defaults={
        "username": "adriana",
        "nombre": "Adriana Ayllón Pardo",
        "rol": "admin",
        "activo": True,
        "is_active": True,
        "is_staff": True,
        "is_superuser": True
    }
)

administradora.set_unusable_password()
administradora.save()

# CASETAS

casetas = [
    ("Caseta Achica Arriba", "La Paz"),
    ("Caseta Autopista", "La Paz - El Alto"),
    ("Caseta Río Seco", "El Alto"),
]

for nombre, ubicacion in casetas:

    Caseta.objects.get_or_create(
        nombre=nombre,
        defaults={
            "ubicacion": ubicacion
        }
    )


# TARIFAS DE PRUEBA

tarifas = [
    ("moto", 2, 2),
    ("auto", 2, 5),
    ("minibus", 2, 8),
    ("bus", 2, 12),
    ("bus", 3, 18),
    ("camion", 2, 10),
    ("camion", 3, 15),
    ("camion", 4, 20),
    ("camion", 5, 25),
    ("camion", 6, 30),
]

for categoria, ejes, monto in tarifas:

    Tarifa.objects.update_or_create(
        categoria=categoria,
        ejes=ejes,
        defaults={
            "monto": Decimal(str(monto))
        }
    )


# VEHÍCULOS FICTICIOS DE PRUEBA

vehiculos = [
    ("1234ABC", "Juan Pérez", "auto", 2, 100),
    ("2345BCD", "María López", "auto", 2, 50),
    ("3456CDE", "Carlos Mamani", "auto", 2, 0),
    ("4567DEF", "Ana Quispe", "auto", 2, 80),
    ("5678EFG", "Pedro Flores", "auto", 2, 30),
    ("6789FGH", "Luis Vargas", "moto", 2, 20),
    ("7890GHI", "Lucía Rojas", "moto", 2, 0),
    ("8901HIJ", "Mario Condori", "moto", 2, 40),
    ("9012IJK", "Elena Castro", "minibus", 2, 100),
    ("1023JKL", "José Ramos", "minibus", 2, 60),
    ("2034KLM", "Rosa Choque", "minibus", 2, 0),
    ("3045LMN", "Pablo Cruz", "minibus", 2, 90),
    ("4056MNO", "Empresa Alfa", "bus", 2, 200),
    ("5067NOP", "Empresa Beta", "bus", 3, 150),
    ("6078OPQ", "Empresa Gamma", "bus", 2, 0),
    ("7089PQR", "Transporte Uno", "camion", 2, 300),
    ("8090QRS", "Transporte Dos", "camion", 3, 250),
    ("9101RST", "Transporte Tres", "camion", 4, 100),
    ("1122STU", "Transporte Cuatro", "camion", 5, 0),
    ("2233TUV", "Transporte Cinco", "camion", 6, 500),
]

for placa, propietario, categoria, ejes, saldo in vehiculos:

    Vehiculo.objects.update_or_create(
        placa=placa,
        defaults={
            "propietario": propietario,
            "categoria": categoria,
            "ejes": ejes,
            "saldo": Decimal(str(saldo)),
            "activo": True
        }
    )


print("DATOS INICIALES CREADOS")
print("Usuarios:", Usuario.objects.count())
print("Vehículos:", Vehiculo.objects.count())
print("Casetas:", Caseta.objects.count())
print("Tarifas:", Tarifa.objects.count())