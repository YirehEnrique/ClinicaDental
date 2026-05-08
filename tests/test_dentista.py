import pytest
from paciente.models import Usuario
from dentista.models import Dentista

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