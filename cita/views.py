from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from .forms import FormCita
from .models import Cita
from .models import Dentista
from .models import EstadoCita
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

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
                            messages.error(request, f"{error}")

        elif accion == 'completada':
            cita = Cita.objects.get(id=cita_id)
            cita.estado_cita_id = 2  # Confirmada
            cita.save()
        elif accion == 'cancelar':
            cita = Cita.objects.get(id=cita_id)
            cita.estado_cita_id = 3  # Cancelada
            cita.save()

        
        elif accion == 'reprogramar':
            # 1. Obtenemos la cita original (usamos get_object_or_404 por seguridad)
            cita = get_object_or_404(Cita, id=cita_id)
            
            # 2. INSTANCIAMOS EL FORMULARIO
            # - request.POST: Contiene la nueva fecha y hora que envió el usuario.
            # - instance=cita_a_editar: Le dice al form que es una EDICIÓN. 
            #   Esto activa tu lógica de "exclude(pk=self.instance.pk)" para que no choque consigo misma.
            form= FormCita(request.POST, instance=cita)
            
            # 3. VALIDAMOS
            if form.is_valid():
                # Si pasa la validación de los 30 mins, preparamos el guardado
                citag = form.save(commit=False)
                
                # Restablecemos el estado a "Pendiente" (ID 1)
                citag.estado_cita_id = 1 
                
                # Guardamos definitivamente en la BD
                citag.save()
                
                messages.info(request, "Cita reprogramada correctamente.")
            else:
                # 4. SI FALLA (Choque de horario u otro error)
                # Extraemos los errores del formulario y los mostramos como alertas rojas
                for field, errors in form.errors.items():
                    for error in errors:
                        # Esto mostrará: "Choque de horario: Ya existe una cita a las..."
                        messages.error(request, error)
            
            return redirect('cita')

        
        return redirect(f"/cita?fecha={fechas}&estado={estado}&page={page_obj.number}")
    else:
        form=  FormCita() 

    context = {
        'form': form,
        'page_obj': page_obj,
        'estados': EstadoCita.objects.all(),
        'dentistas': Dentista.objects.all(),
        'estado': estado,
        'fechas': fechas,
    }
    return render(request, 'cita.html', context)

