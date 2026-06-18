import pytest
from django.urls import reverse
from django.core import mail

from django.contrib.auth.tokens import (default_token_generator)
from django.utils.http import (urlsafe_base64_encode)
from django.utils.encoding import force_bytes

from paciente.models import Paciente, Usuario

# ------------ #Definiendo la información que normalmente se va a manerja # ------------ #
@pytest.fixture
def admin_user():
    return Usuario.objects.create_user(
        username='admin',
        password='123456',
        rol='ad'
    )

@pytest.fixture
def dentista_user():
    return Usuario.objects.create_user(
        username='dentista',
        password='123456',
        email='dentista@gmail.com',
        rol='de'
    )


# ------------ # Tests Para Login (administrador, dentista y usuario inexistente) # ------------ #
@pytest.mark.django_db
def test_login_admin_exitoso(client, admin_user):

    response = client.post(
        reverse('login'),
        {
            'username': 'admin',
            'password': '123456'
        }
    )
    assert response.status_code == 302
    assert response.url == reverse('admin:index')

@pytest.mark.django_db
def test_login_dentista_exitoso(client, dentista_user):

    response = client.post(
        reverse('login'),
        {
            'username': 'dentista',
            'password': '123456'
        }
    )
    assert response.status_code == 302
    assert response.url == reverse('cita')

@pytest.mark.django_db
def test_login_usuario_no_existe(client):

    response = client.post(
        reverse('login'),
        {
            'username': 'usuario_100__no_fake',
            'password': '123456'
        }
    )
    assert response.status_code == 200
    mensajes = list(response.wsgi_request._messages)
    assert any(
        'Usuario No Existe' in str(m)
        for m in mensajes
    )


# ------------ # Tests Para Login Recuperar Contraseña y Cambiarla (Una vez logeado) # ------------ #

@pytest.mark.django_db
def test_recuperar_password_correos_no_coinciden(client):

    response = client.post(
        reverse('recuperar_contra'),
        {
            'email1': 'test@gmail.com',
            'email2': 'otro@gmail.com'
        }
    )
    assert response.status_code == 200
    assert (
        'Los correos no coinciden'
        in response.content.decode()
    )

@pytest.mark.django_db
def test_recuperar_password_usuario_no_existe(client):

    response = client.post(
        reverse('recuperar_contra'),
        {
            'email1': 'fake@gmail.com',
            'email2': 'fake@gmail.com'
        }
    )
    assert response.status_code == 200
    assert (
        'Usuario no existe'
        in response.content.decode()
    )

@pytest.mark.django_db
def test_recuperar_password_envia_email(client,dentista_user):

    response = client.post(
        reverse('recuperar_contra'),
        {
            'email1': dentista_user.email,
            'email2': 'dentista@gmail.com'
        }
    )
    assert response.status_code == 200
    assert len(mail.outbox) == 1
    email = mail.outbox[0]

    assert (
        email.subject
        == 'Recuperación de contraseña'
    )

    assert (
        'restablecer tu contraseña'
        in email.body
    )

@pytest.mark.django_db
def test_reset_password_token_valido(client, dentista_user):

    uid = urlsafe_base64_encode(
        force_bytes(dentista_user.pk)
    )
    token = default_token_generator.make_token(
        dentista_user
    )
    response = client.get(
        reverse(
            'reset_password_confirm',
            args=[uid, token]
        )
    )

    assert response.status_code == 200
    assert (
        'validlink'
        in response.context
    )
    assert response.context['validlink'] is True

@pytest.mark.django_db
def test_cambio_password_exitoso(client,dentista_user):

    client.force_login(dentista_user)
    response = client.post(
        reverse('cambio_contra'),
        {
            'actual': '123456',
            'nueva': 'nueva123',
            'confirm_nueva': 'nueva123'
        }
    )
    dentista_user.refresh_from_db()
    assert response.status_code == 200
    assert dentista_user.check_password(
        'nueva123'
    )

@pytest.mark.django_db
def test_cambio_password_actual_incorrecta(client,dentista_user):
    client.force_login(dentista_user)
    response = client.post(
        reverse('cambio_contra'),
        {
            'actual': 'incorrecta',
            'nueva': 'nueva123',
            'confirm_nueva': 'nueva123'
        }
    )
    assert (
        'Contraseña Actual incorrecta'
        in response.content.decode()
    )


@pytest.mark.django_db
def test_cambio_password_no_coinciden(client,dentista_user):
    client.force_login(dentista_user)
    response = client.post(
        reverse('cambio_contra'),
        {
            'actual': '123456',
            'nueva': 'nueva123',
            'confirm_nueva': 'otra'
        }
    )
    assert (
        'no coinciden'
        in response.content.decode()
    )