from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import Formpaciente
from .models import Paciente
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cita.models import Cita
from tratamientos.models import PlanTratamiento

@login_required
def paciente(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        paciente_id = request.POST.get('paciente_id')

        if accion == 'guardar':
            form = Formpaciente(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Paciente registrado exitosamente.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{error}")
        elif accion == 'editar':
            paciente_obj = get_object_or_404(Paciente, id=paciente_id)
            form = Formpaciente(request.POST, instance=paciente_obj)
            
            if form.is_valid():
                form.save()
                messages.success(request, "Datos del paciente actualizados.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{error}")
        return redirect('paciente')
    else:
        form = Formpaciente()
        
    q = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.all().order_by('-id').prefetch_related(
        'cita_set', 
        'cita_set__estado_cita',
        'plantratamiento_set',
        'plantratamiento_set__tratamiento'
    )

    if q:
        pacientes = pacientes.filter(
            Q(nb1__icontains=q) | 
            Q(nb2__icontains=q) | 
            Q(ap1__icontains=q) | 
            Q(ap2__icontains=q) | 
            Q(telefono__icontains=q) | 
            Q(correo__icontains=q)
        )

    paginator = Paginator(pacientes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form, 
        'page_obj': page_obj, 
        'q': q,
        'cita': Cita.objects.all(),
        'tratamiento': PlanTratamiento.objects.all(),
    }

    return render(request, 'paciente.html', context)