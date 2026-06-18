import pytest
from django.db import connection

from paciente.models import Paciente

# ------------ # Test Conexión a la base de datos # ------------ #
@pytest.mark.django_db
def test_conexion_bd():
    with connection.cursor() as cursor:

        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()

    assert resultado[0] == 1

# ------------ # Test Escritura en la base de datos # ------------ #
@pytest.mark.django_db
def test_escritura_base_datos():

    paciente = Paciente.objects.create(
        nb1='Juan',
        ap1='Perez',
        telefono='88887777',
        correo='juan@gmail.com',
        sexo='M'
    )

    assert paciente.id is not None