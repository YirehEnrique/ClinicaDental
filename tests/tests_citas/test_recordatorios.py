import pytest
from django.urls import reverse
from django.utils import timezone 
from unittest.mock import patch

from paciente.models import Paciente, Usuario
from dentista.models import Dentista
from cita.models import Cita, TipoCita, EstadoCita

# ------------ #Definiendo la información que normalmente se va a manerja # ------------ #
@pytest.fixture
def usuario():
    return Usuario.objects.create_user(
        username="dentista1",
        password="123456",
        rol="de"
    )

@pytest.fixture
def dentista(usuario):
    return Dentista.objects.create(
        usuario=usuario,
        nb1="Mario",
        ap1="Perez",
        telefono="88887777",
        correo="mario@gmail.com",
        sexo="M",
        cedula="001-010101-0003C"
    )

@pytest.fixture
def paciente():
    return Paciente.objects.create(
        nb1="Juan",
        ap1="Lopez",
        telefono="88886666",
        correo="juan@gmail.com",
        sexo="M"
    )

@pytest.fixture
def tipo_cita():
    return TipoCita.objects.create(
        tipo="Consulta General",
        precio=25.00
    )

@pytest.fixture
def estados_cita():
    pendiente = EstadoCita.objects.create(
        id=1,
        estado="Pendiente"
    )

    completada = EstadoCita.objects.create(
        id=2,
        estado="Completada"
    )

    cancelada = EstadoCita.objects.create(
        id=3,
        estado="Cancelada"
    )

    return {
        "pendiente": pendiente,
        "completada": completada,
        "cancelada": cancelada
    }

@pytest.fixture 
def cita(dentista, paciente, tipo_cita, estados_cita):
    #fecha_ok = make_aware(datetime(2026, 5, 10, 0, 0, 0))
    return Cita.objects.create(
        paciente=paciente,
        dentista=dentista,
        tipo_cita=tipo_cita,
        estado_cita=estados_cita["pendiente"],
        precio_cita=25.00,
        fecha=timezone.now()
    )

@pytest.fixture 
def cliente_autenticado(client, usuario):
    client.force_login(usuario)
    return client

# ------------ # Test Habilitar Recordatorios # ------------ #

@pytest.mark.django_db
@patch('cita.views.smtplib.SMTP_SSL')
def test_enviar_recordatorio_correo(mock_smtp, cliente_autenticado, cita):
    response = cliente_autenticado.post(
        reverse('cita'),
        {
            'accion': 'agendar_notificacion',
            'cita_id': cita.id,
            'metodo': 'correo',
            'hora': 10,
            'minutos': 30,
            'fecha': '2026-05-20'
        }
    )
    assert response.status_code == 302
    assert mock_smtp.called

@pytest.mark.django_db
@patch('cita.views.enviar_whatsapp_async')
def test_enviar_recordatorio_whatsapp(mock_whatsapp, cliente_autenticado, cita):
    response = cliente_autenticado.post(
        reverse('cita'),
        {
            'accion': 'agendar_notificacion',
            'cita_id': cita.id,
            'metodo': 'whatsapp',
            'hora': 10,
            'minutos': 30,
            'fecha': '2026-05-20'
        }
    )
    assert response.status_code == 302
    assert mock_whatsapp.called