import threading
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import FormDentista
from .models import Dentista
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages 
from django.core.mail import EmailMessage
from django.conf import settings

def enviar_email_cambio_contra_bg(email_obj):
    try:
        email_obj.send(fail_silently=False)
        print("=== [ÉXITO] El correo de cambio de contraseña se envió correctamente ===")
    except Exception as e:
        print(f"=== [ERROR SMTP] No se pudo enviar el correo de cambio de contraseña: {e} ===")

@login_required
def dentista(request): 
    if request.method == 'POST':
        accion = request.POST.get('accion')
        dentista_id = request.POST.get('dentista_id')
        if accion == 'guardar':
            form = FormDentista(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Dentista registrado correctamente.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{error}")
        elif accion == 'editar':
            dentista_obj = get_object_or_404(Dentista, id=dentista_id)
            form = FormDentista(request.POST, instance=dentista_obj)
            
            if form.is_valid():
                form.save()
                messages.success(request, "Datos del dentista actualizados.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{error}")
        
        elif accion == 'cambiar_estado':
            dentista = get_object_or_404(Dentista, id=dentista_id)

            dentista.estado = not dentista.estado 
            dentista.save()
            
            # Usamos 'warning' si se desactiva para que llame la atención
            if dentista.estado:
                messages.success(request, f"Dentista {dentista.nb1} {dentista.ap1} activado.")
            else:
                messages.warning(request, f"Dentista {dentista.nb1} {dentista.ap1} desactivado.")

        return redirect('dentista')

    else:
        form = FormDentista()

        q = request.GET.get('q', '').strip()
        dentistas = Dentista.objects.all().order_by('-id') 

        if q:
            dentistas = dentistas.filter(
                Q(nb1__icontains=q) | 
                Q(nb2__icontains=q) | 
                Q(ap1__icontains=q) | 
                Q(ap2__icontains=q) | 
                Q(telefono__icontains=q) | 
                Q(correo__icontains=q)
            )
        
        paginator = Paginator(dentistas, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'dentista.html', {
            'form': form, 
            'page_obj': page_obj, 
            'q': q
        })

@login_required
def perfil_dentista(request):
    # try: 
    #     dentista = request.user.dentista
    # except:
    #     return redirect("login") 
    
    if request.user.rol == "de":
        dentista = request.user.dentista
        context = {
            "nombre": dentista.nb1,
            "apellido": dentista.ap1,
            "telefono": dentista.telefono,
            "correo": dentista.correo
        }
        return render(request, "perfil_dentista.html", {"dentista": dentista})
    #Este else puede causar error creo 
    else:
        return redirect("login") #Aquí redireccionamos al login, pero como ya está iniciado en sesión, ps va a citas.

@login_required
def cambio_contra(request):
    if request.method == 'POST':
        #Obtenemos los tres campos, la contraseña actual, su confirmación y la nueva contraseña.
        current_password = request.POST.get('actual')
        nueva_password = request.POST.get('nueva')
        confirma_nueva_password = request.POST.get('confirm_nueva')

        #recuperamos el usuario que está intentando cambiar la contraseña
        user = request.user

        #Comprobando que no estén vacíos
        if not current_password or not nueva_password or not confirma_nueva_password:
            return render(request, "cambio_contra.html", {
                "error": "Los campos no pueden estar vacíos"
            })
        
        #Comprobamos que las contraseñas actuales ingresadas coincidan
        if nueva_password != confirma_nueva_password:
            return render(request, "cambio_contra.html", {"error": "Los campos de la nueva contraseña no coinciden"})
        
        #Comprobamos que la contraseña ingresada (actual) coincida con la que está en la base de datos
        if not user.check_password(current_password):
            return render(request, "cambio_contra.html", {"error": "Contraseña Actual incorrecta"})

        user.set_password(nueva_password)
        user.save()

        # Evitar cerrar sesión
        update_session_auth_hash(request, user)

        # Enviar correo de aviso
        if user.email is not None:
            email_sender = settings.EMAIL_HOST_USER
            email_reciver = user.email
            subject = 'Aviso de cambio de contraseña'
            body = f"Este es un aviso de que se cambió su contraseña de Clinica Dental Solis"
            #Elaboramos el mensaje del correo
            email = EmailMessage(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [email_reciver]
            )
            #Enviamos el correo
            hilo = threading.Thread(target=enviar_email_cambio_contra_bg, args=(email,))
            hilo.start()
            #email.send(fail_silently=False) #Ese atributo es para ver si hay algún error lo muestre en consola
            return render(request, "cambio_contra.html", {"mensaje": "Contraseña cambiada con éxito, se envió un correo"})
        return render(request, "cambio_contra.html", {"mensaje": "Contraseña cambiada con éxito"})
    return render(request, "cambio_contra.html")



""" Esto es para mostrar el modulo de doctores xd
<li class="nav-item">
    <a class="nav-link {% if request.resolver_match.url_name == 'dentista' %}active{% endif %}"
        href="{% url 'dentista' %}">Dentista</a>
</li>
"""