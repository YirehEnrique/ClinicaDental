import pytest
from django.urls import reverse
from django.utils import timezone 

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

@pytest.fixture #Para forzar una autenticación 
def cliente_autenticado(client, usuario):
    client.force_login(usuario)
    return client

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

# ------------ # Test Registrar Cita # ------------ #
@pytest.mark.django_db
def test_registrar_cita(dentista, paciente, tipo_cita, estados_cita):
    cita = Cita.objects.create(
        paciente=paciente,
        dentista=dentista,
        tipo_cita=tipo_cita,
        estado_cita=estados_cita["pendiente"],
        precio_cita=25.00,
        fecha=timezone.now()
    )
    assert cita.paciente.nb1 == "Juan"
    assert cita.dentista.nb1 == "Mario"
    assert cita.tipo_cita.tipo == "Consulta General"
    assert cita.estado_cita.estado == "Pendiente"
    assert Cita.objects.count() == 1

# ------------ # Test Validar Reprogramar, Confirmar y Cancelar Cita # ------------ #

@pytest.mark.django_db
def test_confirmar_cita(cliente_autenticado, cita):
    response = cliente_autenticado.post(
        reverse('cita'),
        {
            'accion': 'completada',
            'cita_id': cita.id
        }
    )
    cita.refresh_from_db()
    assert response.status_code == 302
    assert cita.estado_cita.id == 2

@pytest.mark.django_db
def test_cancelar_cita(cliente_autenticado, cita):
    response = cliente_autenticado.post(
        reverse('cita'),
        {
            'accion': 'cancelar',
            'cita_id': cita.id
        }
    )
    cita.refresh_from_db()
    assert response.status_code == 302
    assert cita.estado_cita.id == 3

@pytest.mark.django_db
def test_reprogramar_cita(cliente_autenticado, cita, paciente, dentista, tipo_cita):
    #Agregando la nueva fecha y hora xd
    nueva_fecha = "2026-05-20"
    nueva_hora = "15:30"
    response = cliente_autenticado.post(
        reverse('cita'),
        {
            'accion': 'reprogramar',
            'cita_id': cita.id,
            'fecha': nueva_fecha,
            'hora': nueva_hora,
            'paciente': paciente.id,
            'dentista': dentista.id,
            'tipo_cita': tipo_cita.id,
            'precio_cita': 25.00,
            'notas': 'Cita reprogramada'
        }
    )

    cita.refresh_from_db()
    assert response.status_code == 302
    assert str(cita.fecha.date()) == nueva_fecha
    assert str(cita.hora) == "15:30:00"
    # Debe volver a pendiente
    assert cita.estado_cita.id == 1

#Para validar que se esté correctamente logeado para gestionar las citas. (opcional)
@pytest.mark.django_db
def test_cita_requiere_login(client):
    response = client.get(reverse('cita'))
    assert response.status_code == 302

# ------------ # Test Editar Cita # ------------ #
@pytest.mark.django_db
def test_admin_editar_cita(client, admin_user, cita, paciente, tipo_cita, estados_cita, dentista):

    client.force_login(admin_user)
    url = reverse(
        'admin:cita_cita_change',
        args=[cita.id]
    )
    response = client.post(
        url,
        {
            'accion': 'cancelar',
            'cita_id': cita.id,
            'paciente': paciente.id,
            'dentista': dentista.id,
            'tipo_cita': tipo_cita.id,
            'estado_cita': estados_cita["cancelada"].id,
            'precio_cita': 25.00,
            'fecha': '2026-05-20',
            'hora': '15:30:00',
            'fecha_0': '2026-05-20',
            'fecha_1': '15:30:00',
            'creada_0': '2026-05-10',
            'creada_1': '00:00:00',
            '_save': 'Save'
        }
    )
    if response.status_code != 302:
        print("\n--- ERRORES DETECTADOS ---")
        print(response.context_data['adminform'].form.errors)
        print("--------------------------")
    cita.refresh_from_db()
    assert response.status_code == 302
    assert cita.precio_cita == 25.00