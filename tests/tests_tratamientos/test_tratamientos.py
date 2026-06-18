import pytest
from django.urls import reverse

from tratamientos.models import TipoTratamiento, PlanTratamiento
from paciente.models import Paciente, Usuario
from dentista.models import Dentista

# ------------ # Información Necesaria # ------------ #
@pytest.fixture
def paciente():
    return Paciente.objects.create(
        nb1="Juan",
        ap1="El Doe",
        telefono="12124455",
        correo="juanED@gmail.com",
        sexo="M"
    )

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
def tipo_tratamiento():
    return TipoTratamiento.objects.create(
        nombre="Limpieza Dental",
        precio_estimado=50.00
    )

@pytest.fixture
def Ptratamiento(paciente, dentista, tipo_tratamiento):
    return PlanTratamiento.objects.create(
        tratamiento = tipo_tratamiento,
        paciente = paciente,
        dentista = dentista,
        precio_estimado = tipo_tratamiento.precio_estimado,
    )

# ------------ # Test para Registrar Tratamientos # ------------ #
@pytest.mark.django_db
def test_registrar_tratamiento(paciente, dentista, tipo_tratamiento):
    
    Ptratamiento = PlanTratamiento.objects.create(
        tratamiento = tipo_tratamiento,
        paciente = paciente,
        dentista = dentista,
        precio_estimado = tipo_tratamiento.precio_estimado,
    )
    assert Ptratamiento.tratamiento.nombre == "Limpieza Dental"
    assert Ptratamiento.paciente.nb1 == "Juan"
    assert Ptratamiento.dentista.nb1 == "Mario"
    assert Ptratamiento.tratamiento.precio_estimado == 50
    assert TipoTratamiento.objects.count() == 1


@pytest.mark.django_db
def test_admin_editar_tratamiento(client, admin_user,Ptratamiento):

    client.force_login(admin_user)
    url = reverse(
        'admin:tratamientos_plantratamiento_change',
        args=[Ptratamiento.id]
    )
    response = client.post(
        url,
        {
            'tratamiento': Ptratamiento.tratamiento.id,
            'paciente': Ptratamiento.paciente.id, 
            'dentista': Ptratamiento.dentista.id,
            'notas': 'Extracción Dental',
            'precio_estimado': 100,
            'sesiones_estimadas': 2,
            'sesiones_realizadas': 0,
            'estado': 'C',
            #Fechas por si acaso
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
    Ptratamiento.refresh_from_db()
    assert response.status_code == 302
    assert Ptratamiento.notas == 'Extracción Dental'
    assert Ptratamiento.precio_estimado == 100