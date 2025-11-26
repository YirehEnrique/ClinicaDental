from django.core.paginator import Paginator
from django.shortcuts import render, redirect
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
        fechas = timezone.now().date()-timezone.timedelta(days=1)
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
        elif accion == 'completada':
            cita = Cita.objects.get(id=cita_id)
            cita.estado_cita_id = 2  # Confirmada
            cita.save()
        elif accion == 'cancelar':
            cita = Cita.objects.get(id=cita_id)
            cita.estado_cita_id = 3  # Cancelada
            cita.save()
        elif accion == 'reprogramar':
            cita = Cita.objects.get(id=cita_id)
            cita.fecha = request.POST.get('fecha')
            cita.hora = request.POST.get('hora')
            cita.estado_cita_id = 1
            cita.save()
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

