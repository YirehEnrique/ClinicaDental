from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from .forms import FormCita
from .models import Cita
from .models import Dentista
from .models import EstadoCita
from .models import TipoCita
from django.utils import timezone
from django.contrib.auth.decorators import login_required

import pywhatkit
import datetime
import threading
import time

from email.message import EmailMessage
import ssl
import smtplib

import logging
from django.contrib import messages

#Importamos para usar el json.dumps(...)
import json

# Create your views here.

def enviar_whatsapp_async(telefono, mensaje):
    def task():
        try:
            import pywhatkit
            pywhatkit.sendwhatmsg_instantly(
                telefono,
                mensaje,
                wait_time=25,     
                tab_close=True    
            )
        except Exception as e:
            print("Error al enviar WhatsApp:", e)

    threading.Thread(target=task).start()

@login_required
def cita(request):
    citas = Cita.objects.all().order_by('fecha', 'hora','-estado_cita__estado')

    if(request.GET.get('fecha') is None):
        fechas = timezone.now().date()
    else:
        fechas = request.GET.get('fecha')

    if(request.GET.get('estado') is None):
        estado = 'Pendiente'
    elif request.GET.get('estado') == 'Todos':
        estado = ''
    else:
        estado = request.GET.get('estado')


    if estado:
        citas = citas.filter(estado_cita__estado=estado)
    if fechas:
        citas = citas.filter(fecha=fechas)


    paginator = Paginator(citas, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #Sección de horas y minutos
    hours = list(range(0, 24))                  
    minutes = list(range(0, 60))#["00","5","10","15","20","25","30","35","40","45","50","55"]


    if request.method == 'POST':
        form = FormCita(request.POST)

        accion = request.POST.get('accion')
        cita_id = request.POST.get('cita_id')

        if accion == 'guardar':
            if form.is_valid():
                form.save()
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            messages.error(request, f"hay un error quien sabe donde{error}")

        elif accion == 'completada':
            cita = Cita.objects.get(id=cita_id)
            cita.estado_cita_id = 2  # Confirmada
            cita.save()
        elif accion == 'cancelar':
            cita = Cita.objects.get(id=cita_id)
            cita.estado_cita_id = 3  # Cancelada 
            cita.save()

        
        elif accion == 'reprogramar':
            cita = get_object_or_404(Cita, id=cita_id)
            
            datos = {
                'paciente': cita.paciente.id,
                'dentista': cita.dentista.id,
                'tipo_cita': cita.tipo_cita.id,
                'precio_cita': cita.precio_cita,
                'notas': cita.notas,
                'estado_cita': 1, # Forzamos a Pendiente
            }
            datos.update(request.POST.dict())

            form= FormCita(datos, instance=cita)

            if form.is_valid():
                citag = form.save(commit=False)
                
                citag.estado_cita_id = 1 
                
                citag.save()
                
                messages.info(request, "Cita reprogramada correctamente.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {field}: {error}")
            
            return redirect('cita')

        elif accion == 'agendar_notificacion':
            #Partes generales
            cita = Cita.objects.get(id=cita_id)
            metodo = request.POST.get('metodo')
            paciente = cita.paciente
            email = paciente.correo
            telefono = "+505" + paciente.telefono
            
            #Para el WhatsApp
            hora = int(request.POST.get('hora'))           
            minutos = int(request.POST.get('minutos'))
            fecha_post = request.POST.get('fecha')    
            fecha_text = cita.fecha.strftime("%d de %B de %Y") if cita.fecha else (fecha_post or "")
            
            #Para el Correo
            PASSWORD = "xotn bvly wdjj anjl"
            email_sender = "enriquemedina880@gmail.com"
            email_reciver = email
            subject= "Recordatorio de Cita Dental"
            #hora_display_correo = f"{hora:02d}:{minutos:02d}"
            body = f"Recordatorio: Su cita está agendada para el {fecha_text} para las {cita.hora}"

            if metodo == "correo":
                em = EmailMessage()
                em["From"] = email_sender
                em["To"] = email_reciver
                em["Subject"] = subject
                em.set_content(body)
                context_email = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context= context_email) as smtp:
                    smtp.login(email_sender, PASSWORD)
                    smtp.sendmail(email_sender, email_reciver,em.as_string())
                
                pass  

            elif metodo == "whatsapp":
                mensaje = f"Recordatorio: Su cita está agendada para el {fecha_text} a las {cita.hora}. Clínica Dental."
                
                ahora = datetime.datetime.now()
                if hora < ahora.hour or (hora == ahora.hour and minutos <= ahora.minute):
                    # mínimo 2 minutos en el futuro
                    hora  = ahora.hour 
                    minutos = (ahora.minute + 2) % 60
                try: 
                    #minutos = hora.minute
                    enviar_whatsapp_async(telefono, mensaje)
                    #pywhatkit.sendwhatmsg(telefono, mensaje, hora, minutos, 5)
                except Exception as e:
                    messages.error(request, f"No fue posible enviar WhatsApp: {e}")
                pass  
        
        return redirect(f"/cita?fecha={fechas}&estado={estado}&page={page_obj.number}")
    else:
        form=  FormCita() 

    #Guardamos el precio de las citas (según su tipo) en un diccionario
    dict_precios = {tipo.id : float(tipo.precio) for tipo in TipoCita.objects.all()}

    context = {
        'form': form,
        'page_obj': page_obj,
        'estados': EstadoCita.objects.all(),
        'dentistas': Dentista.objects.all(),
        'estado': estado,
        'fechas': fechas,
        'hours': hours,
        'minutes': minutes,
        'precios_json': json.dumps(dict_precios), #Enviamos los precios de las citas xd 
    }
    return render(request, 'cita.html', context)