from urllib import request
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import FormPlanTratamiento, FormPlanItems
from .models import PlanTratamiento, PlanItems, ItemSesion
from django.db.models import Q
from cita.forms import FormCita
from cita.models import Cita
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
@login_required
def tratamiento(request):

    formTratamiento = FormPlanTratamiento()
    formItem = FormPlanItems()
    formCita = FormCita()

    q = request.GET.get('q', '').strip()
    tratamientos = PlanTratamiento.objects.all().order_by('-estado', '-creada').prefetch_related('plan_items', 'plan_items__itemsesion_set', 'plan_items__itemsesion_set__cita')
    accion = request.POST.get('accion')

    if request.method == 'POST':
        cita_id=request.POST.get('cita_id')
        if accion == 'guardarTratamiento':
            formTratamiento=FormPlanTratamiento(request.POST)        
            if formTratamiento.is_valid():
                formTratamiento.save()
                messages.success(request, "Tratamiento creado correctamente.")
                return redirect('tratamiento')
            else:
                for field, errors in formTratamiento.errors.items():
                    for error in errors:
                        messages.error(request, error)
        elif accion == 'guardarItem':
            tratamiento_id=request.POST.get('tratamiento_id')
            plan_tratamiento= get_object_or_404(PlanTratamiento, id=tratamiento_id)
            formItem=FormPlanItems(request.POST)
    
            if formItem.is_valid():
                nuevo_item=formItem.save(commit=False)
                nuevo_item.plan_tratamiento=plan_tratamiento

                ultimo_plan_item=PlanItems.objects.filter(plan_tratamiento=plan_tratamiento).order_by('-orden').first()

                if ultimo_plan_item:
                    nuevo_item.orden = ultimo_plan_item.orden + 1
                else:
                    nuevo_item.orden = 1
                    nuevo_item.save()
                    messages.success(request, "Fase agregada correctamente.")
                    return redirect('tratamiento')
            else:
                for field, errors in formItem.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, f"{error}")
                        else:
                            messages.error(request, f"{error}")


        elif accion=="agendarCita":
            item_id=request.POST.get('item_id')
            formCita=FormCita(request.POST)
            if formCita.is_valid():
                nueva_cita=formCita.save()
                ItemSesion.objects.create(plan_item_id=item_id,cita_id=nueva_cita.id)
                messages.success(request, "Cita agendada.")
                return redirect('tratamiento')
            else:
                for field, errors in formCita.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, f"{error}")
                        else:
                            messages.error(request, f"{error}")

        elif accion in ['completada', 'cancelar', 'reprogramar']:
            cita = get_object_or_404(Cita, id=cita_id)

            if accion == 'completada':
                if cita.estado_cita_id == 3:
                    messages.error(request, "No puedes completar una cita que está Cancelada.")
                elif cita.estado_cita_id == 2:
                    messages.warning(request, "Esta cita ya estaba marcada como Completada.")
                else:
                    cita.estado_cita_id = 2
                    cita.save()
                    messages.success(request, "Cita completada con éxito.")

            elif accion == 'cancelar':
                if cita.estado_cita_id == 2:
                    messages.error(request, "No puedes cancelar una cita que ya fue Completada.")
                elif cita.estado_cita_id == 3:
                    messages.warning(request, "La cita ya estaba cancelada.")
                else:
                    cita.estado_cita_id = 3
                    cita.save()
                    messages.warning(request, "La cita ha sido cancelada.")

            elif accion == 'reprogramar':
                cita = get_object_or_404(Cita, id=cita_id)
                form= FormCita(request.POST, instance=cita)

                if form.is_valid():
                    citag = form.save(commit=False)
                    
                    citag.estado_cita_id = 1 
                    
                    citag.save()
                    
                    messages.info(request, "Cita reprogramada correctamente.")
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, error)
        

            return redirect('tratamiento')
    if q:
        tratamientos = tratamientos.filter(
            Q(tratamiento__nombre__icontains=q) |  
            Q(paciente__nb1__icontains=q) |
            Q(paciente__nb2__icontains=q) |
            Q(paciente__ap1__icontains=q) |
            Q(paciente__ap2__icontains=q) |
            Q(dentista__nb1__icontains=q) |
            Q(dentista__nb2__icontains=q) |
            Q(dentista__ap1__icontains=q) |
            Q(dentista__ap2__icontains=q) |
            Q(paciente__telefono__icontains=q)
        )

    paginator = Paginator(tratamientos, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'formTratamiento': formTratamiento,
        'formItem':formItem,
        'page_obj':page_obj,
        'q':q,
        'formCita':formCita
    }
    return render(request, 'tratamiento.html', context)