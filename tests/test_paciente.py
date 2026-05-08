import pytest
from paciente.models import Paciente, Usuario

@pytest.mark.django_db
def test_registrar_paciente():

    paciente = Paciente.objects.create(
        nb1="Alberto",
        ap1="Mendoza",
        telefono="88887777",
        correo="enrique@gmail.com",
        sexo="M",
        cedula="0010101010001A"
    )
    assert paciente.nb1 == "Alberto"
    assert paciente.ap1 == "Mendoza"
    assert paciente.telefono == "88887777"
    assert paciente.correo == "enrique@gmail.com"
    assert paciente.sexo == "M"
    assert Paciente.objects.count() == 1



@pytest.mark.django_db
def test_registrar_usuario():

    usuario = Usuario.objects.create_user(
        username="admin",
        password="123456",
        rol="ad"
    )

    assert usuario.username == "admin"
    assert usuario.rol == "ad"

    # Verifica contraseña encriptada
    assert usuario.check_password("123456")

    assert Usuario.objects.count() == 1