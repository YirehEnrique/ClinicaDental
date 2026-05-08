import pytest

from paciente.models import Paciente, Usuario
from dentista.models import Dentista
from cita.models import Cita, TipoCita, EstadoCita

@pytest.mark.django_db
def test_registrar_cita():
    usuario = Usuario.objects.create_user(
        username="dentista1",
        password="123456",
        rol="de"
    )
    dentista = Dentista.objects.create(
        usuario=usuario,
        nb1="Mario",
        ap1="Perez",
        telefono="88887777",
        correo="mario@gmail.com",
        sexo="M",
        cedula="001-010101-0003C"
    )
    paciente = Paciente.objects.create(
        nb1="Juan",
        ap1="Lopez",
        telefono="88886666",
        correo="juan@gmail.com",
        sexo="M"
    )
    tipo_cita = TipoCita.objects.create(
        tipo="Consulta General",
        precio=25.00
    )
    estado = EstadoCita.objects.create(
        estado="Pendiente"
    )
    cita = Cita.objects.create(
        paciente=paciente,
        dentista=dentista,
        tipo_cita=tipo_cita,
        estado_cita=estado,
        precio_cita=25.00
    )
    assert cita.paciente.nb1 == "Juan"
    assert cita.dentista.nb1 == "Mario"
    assert cita.tipo_cita.tipo == "Consulta General"
    assert cita.estado_cita.estado == "Pendiente"
    assert Cita.objects.count() == 1