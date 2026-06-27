import threading
from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import EmailMessage
from django.contrib import messages 
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

from paciente.models import Usuario
# Create your views here.  
# Función auxiliar para enviar el correo sin bloquear la página web
def enviar_email_en_segundo_plano(email_obj):
    try:
        email_obj.send(fail_silently=False)
        print("=== [ÉXITO] El correo se envió correctamente desde el segundo plano ===")
    except Exception as e:
        print(f"=== [ERROR SMTP] No se pudo enviar el correo: {e} ===")

def register_view(request):  
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta Creada existosamente")
            return redirect('citas')
    else: 
        form = UserCreationForm()
    return render(request, 'register.html',{
        'form': form, #Estos son datos que se envian a la plantilla html en el {title},etc
        'title': 'Registro'
    })

def login_view(request):
    if request.user.is_authenticated:
        return redireccion_por_rol(request.user)
        
    if request.method == 'POST':
        print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #return redirect('cita')
            messages.info(request, "Inicio de Sesión Exitoso. Bienvenido.")
            return redireccion_por_rol(user)
        elif user is None:
            messages.error(request, 'Usuario No Existe')
            return render(request, 'login.html', {
                'title': 'Inicio de Sesión'
            })
        else: 
            messages.error(request, 'Usuario o contraseña incorrecto')
            return render(request, 'login.html', {
                'title': 'Inicio de Sesión'
            })

    return render(request, 'login.html', {
        'title': 'Inicio de Sesión'
    })

def redireccion_por_rol(user):
    role = user.rol
    print(role)
    #Administrador se va a admin de django
    if role == 'ad':
        return redirect(reverse('admin:index'))

    # Dentista 
    if role == 'de':
        return redirect('cita')

    if role == 'pa':
        return print("Redireccionando muchas veces")#redirect('login')
    # Si no cumple nada
    return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')


def reset_password_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Usuario.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm = request.POST.get("confirm_password")
            
            #Si las contraseñas no coinciden 
            if password != confirm:
                return render(request, "reset_password_form.html", {
                    "validlink": True,
                    "error": "Las contraseñas no coinciden"
                })

            #Si las contraseñas si coinciden 
            user.set_password(password)
            user.save()
            return redirect('login')

        return render(request, "reset_password_form.html", {"validlink": True})
    else:
        return render(request, "reset_password_form.html", {"validlink": False})

def recuperar_contra(request):
    if request.method == "POST":
        #Obtenemos el correo y su confirmación de correo
        email1 = request.POST.get("email1")
        email2 = request.POST.get("email2")

        #Validamos que coincidan
        if email1 != email2:
            return render(request, "recuperar_contra.html", {"error": "Los correos no coinciden"})
        
        try:
            user = Usuario.objects.get(email=email1)

            # Generar token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Construir enlace
            link = request.build_absolute_uri(
                f"/reset-password/{uid}/{token}/"
            )
            #Email del usuario
            user_email = user.email

            #Cuestiones para enviar el correo 
            #PASSWORD = "xotn bvly wdjj anjl"
            #email_sender = "enriquemedina880@gmail.com"
            email_reciver = user_email
            subject= "Recuperación de contraseña"
            body = f"Hola, haz clic en el siguiente enlace para restablecer tu contraseña: {link}"

            #Elaboramos el mensaje del correo
            email = EmailMessage(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [email_reciver]
            )

            hilo = threading.Thread(target=enviar_email_en_segundo_plano, args=(email,))
            hilo.start()
            #Enviamos el correo
            #email.send(fail_silently=False) #Ese atributo es para ver si hay algún error lo muestre en consola

            return render(request, "recuperar_contra.html", {"mensaje": "Email enviado con éxito"})
        
        except Usuario.DoesNotExist:
            print("Cayo en la excepcion")
            return render(request, "recuperar_contra.html", {"error": "Usuario no existe"})

    return render(request, "recuperar_contra.html")