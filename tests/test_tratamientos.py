import pytest

from tratamientos.models import TipoTratamiento, PlanTratamiento
from paciente.models import Paciente, Usuario
from dentista.models import Dentista

@pytest.mark.django_db
def test_registrar_tratamiento():
    paciente = Paciente.objects.create(
        nb1="Juan",
        ap1="El Doe",
        telefono="12124455",
        correo="juanED@gmail.com",
        sexo="M"
    )
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
    t_tratamiento = TipoTratamiento.objects.create(
        nombre="Limpieza Dental",
        precio_estimado=50.00
    )
    Ptratamiento = PlanTratamiento.objects.create(
        tratamiento = t_tratamiento,
        paciente = paciente,
        dentista = dentista,
        precio_estimado = t_tratamiento.precio_estimado,
    )
    assert Ptratamiento.tratamiento.nombre == "Limpieza Dental"
    assert Ptratamiento.paciente.nb1 == "Juan"
    assert Ptratamiento.dentista.nb1 == "Mario"
    assert Ptratamiento.tratamiento.precio_estimado == 50
    assert TipoTratamiento.objects.count() == 1