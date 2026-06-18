import pytest
from django.urls import reverse

from paciente.forms import Formpaciente
from paciente.models import Paciente

# ------------ #Definiendo la información que normalmente se va a manerja # ------------ #
@pytest.fixture
def datos_validos():
    return {
        'nb1': 'Juan',
        'nb2': 'Carlos',
        'ap1': 'Perez',
        'ap2': 'Lopez',
        'telefono': '88887777',
        'correo': 'juan@gmail.com',
        'sexo': 'M',
        'cedula': '0010101010001A'
    }

# ------------ # Test Validación de Teléfono Sólo Números (hasta 8) # ------------ #
@pytest.mark.django_db
def test_telefono_solo_numeros(datos_validos):

    datos = datos_validos
    datos['telefono'] = '8888ABCD'
    form = Formpaciente(data=datos)

    assert not form.is_valid()
    assert 'telefono' in form.errors

@pytest.mark.django_db
def test_telefono_menos_8_digitos(datos_validos):

    datos = datos_validos
    datos['telefono'] = '1234'
    form = Formpaciente(data=datos)

    assert not form.is_valid()
    assert 'telefono' in form.errors

@pytest.mark.django_db
def test_telefono_valido(datos_validos):

    datos = datos_validos
    datos['telefono'] = '12347788'
    form = Formpaciente(data=datos)

    assert form.is_valid()

@pytest.mark.django_db
def test_correo_invalido(datos_validos):

    datos = datos_validos
    datos['correo'] = 'correo-malo'
    form = Formpaciente(data=datos)

    assert not form.is_valid()
    assert 'correo' in form.errors

@pytest.mark.django_db
def test_correo_duplicado(datos_validos):
    Paciente.objects.create(
        nb1='Mario',
        ap1='Perez',
        telefono='99998888',
        correo='juan@gmail.com',
        sexo='M'
    )
    form = Formpaciente(
        data=datos_validos
    )

    assert not form.is_valid()
    assert 'correo' in form.errors

@pytest.mark.django_db
def test_correo_correcto(datos_validos):
    datos = datos_validos
    datos['correo'] = 'correo_correcto@gmail.com'
    form = Formpaciente(data=datos)

    assert form.is_valid()


@pytest.mark.django_db
def test_cedula_longitud_incorrecta(datos_validos):

    datos = datos_validos
    datos['cedula'] = '123'
    form = Formpaciente(data=datos)

    assert not form.is_valid()
    assert 'cedula' in form.errors

@pytest.mark.django_db
def test_cedula_numeros_invalidos(datos_validos):

    datos = datos_validos
    datos['cedula'] = 'ABCDEFGHIJKLMN'
    form = Formpaciente(data=datos)

    assert not form.is_valid()
    assert 'cedula' in form.errors

@pytest.mark.django_db
def test_cedula_sin_letra_final(datos_validos):

    datos = datos_validos
    datos['cedula'] = '00101010100011'
    form = Formpaciente(data=datos)

    assert not form.is_valid()
    assert 'cedula' in form.errors

@pytest.mark.django_db
def test_cedula_duplicada(datos_validos):
    Paciente.objects.create(
        nb1='Mario',
        ap1='Perez',
        telefono='99998888',
        correo='mario@gmail.com',
        sexo='M',
        cedula='0010101010001A'
    )
    form = Formpaciente(
        data=datos_validos
    )

    assert not form.is_valid()
    assert 'cedula' in form.errors

@pytest.mark.django_db
def test_cedula_correcta(datos_validos):
    
    datos = datos_validos
    datos['cedula'] = '0010101010001M'
    form = Formpaciente(
        data=datos_validos
    )

    assert form.is_valid()