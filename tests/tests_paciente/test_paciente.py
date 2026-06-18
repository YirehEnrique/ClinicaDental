import pytest
from django.urls import reverse

from paciente.models import Paciente, Usuario

# ------------ #Definiendo la información que normalmente se va a manerja # ------------ #
@pytest.fixture
def admin_usuario():
    return Usuario.objects.create_superuser(
        username='admin',
        password='123456',
        email='admin@gmail.com'
    )


# ------------ # Tests Para Registrar Paciente y Usuario # ------------ #
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

# ------------ # Test Validar Editar Usuario, Paciente # ------------ #

@pytest.mark.django_db
def test_admin_editar_usuario(client, admin_usuario):
    usuario = Usuario.objects.create_user(
        username='juan',
        password='123456',
        rol='pa'
    )
    client.force_login(admin_usuario)
    url = reverse(
        'admin:paciente_usuario_change',
        args=[usuario.id]
    )
    #Obtenemos la url de la página y extraer los datos iniciales que tenga.
    get_response = client.get(url)
    form = get_response.context_data['adminform'].form
    
    data = {k: (v if v is not None else '') for k, v in form.initial.items()}
    data.update({
        'username': 'juan_editado',
        'rol': 'ad',
        'is_active': 'on',
        'date_joined_0': '2026-05-10', 
        'date_joined_1': '00:00:00',
        '_save': 'Save',
    })

    response = client.post(url,data)
    if response.status_code != 302:
        print("\n--- ERRORES DETECTADOS ---")
        print(response.context_data['adminform'].form.errors)
        print("--------------------------")

    usuario.refresh_from_db()
    assert response.status_code == 302
    assert usuario.username == 'juan_editado'
    assert usuario.rol == 'ad'