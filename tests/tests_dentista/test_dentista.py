import pytest
from django.urls import reverse

from paciente.models import Usuario
from dentista.models import Dentista


# ------------ #Definiendo la información que normalmente se va a manerja # ------------ #
@pytest.fixture
def usuario(): 
    return Usuario.objects.create_user(
        username='dentista1',
        password='123456'
    )

@pytest.fixture
def dentista(usuario): 
    return Dentista.objects.create(
        usuario=usuario,
        nb1='Mario',
        ap1='Perez',
        telefono='88887777',
        correo='mario@gmail.com',
        sexo='M',
        cedula='001-010101-0001A'
    )

# ------------ # Test Registrar Dentista # ------------ #
@pytest.mark.django_db
def test_registrar_dentista():

    usuario = Usuario.objects.create_user(
        username="dentista1",
        password="123456",
        rol="de"
    )
    dentista = Dentista.objects.create(
        usuario = usuario,
        nb1="Carlos",
        ap1="Lopez",
        telefono="88889999",
        correo="carlos@gmail.com",
        sexo="M",
        cedula="001-010101-0002B"
    )
    assert dentista.usuario.username == "dentista1"
    assert dentista.nb1 == "Carlos"
    assert dentista.ap1 == "Lopez"

    assert Dentista.objects.count() == 1

# ------------ # Test Editar Dentista # ------------ #
@pytest.mark.django_db
def test_admin_editar_dentista(client, admin_user, dentista):
    #Forzamos el login
    client.force_login(admin_user)
    #Vamos a la url
    url = reverse(
        'admin:dentista_dentista_change',
        args=[dentista.id]
    )
    response = client.post(
        url,
        {
            'usuario': dentista.usuario.id,
            'nb1': 'Carlos',
            'nb2': '',
            'ap1': 'Lopez',
            'ap2': '',
            'telefono': '22990456',
            'correo': 'carlos@gmail.com',
            'sexo': 'M',
            'cedula': '001-010101-0001A',
            'estado': True,
            'fecha_0': '2026-05-20',
            'fecha_1': '15:30:00',
            '_save': 'Save' 
        }
    )
    dentista.refresh_from_db()
    assert response.status_code == 302
    assert dentista.nb1 == 'Carlos'
    assert dentista.ap1 == 'Lopez'