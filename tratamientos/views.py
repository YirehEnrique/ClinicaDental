from urllib import request
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import FormPlanTratamiento, FormItemSesion
from .models import PlanTratamiento, ItemSesion, TipoTratamiento
from django.db.models import Q
from cita.forms import FormCita
from cita.models import Cita
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from cita.models import TipoCita

import json

# Create your views here.
@login_required
def tratamiento(request):

    formTratamiento = FormPlanTratamiento()
    formCita = FormCita()
    formSesion = FormItemSesion()

    q = request.GET.get('q', '').strip()
    #Esta consulta permite relacionar directamente los 2 modelos relacionados xd
    tratamientos = PlanTratamiento.objects.all().order_by('-estado', '-creada').select_related('paciente', 'dentista', 'tratamiento').prefetch_related('sesiones__citas') #.prefetch_related('itemsesion_set__cita')
    accion = request.POST.get('accion')
    
    if request.method == 'POST':
        cita_id=request.POST.get('cita_id')
        paciente_id = request.POST.get('paciente_id')

        # if not accion:
        #     return redirect('tratamiento')
        
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
        
        #Este falta editar para que funcione para las Sesiones
        elif accion == 'guardarItem':
            tratamiento_id=request.POST.get('tratamiento_id')
            print(request.POST)
            plan_trat = get_object_or_404(PlanTratamiento, id=tratamiento_id)
            formSesion = FormItemSesion(request.POST)

            if formSesion.is_valid():
                nueva_sesion = formSesion.save(commit=False)    # Crea la instancia sin guardar aún
                nueva_sesion.plan_tratamiento = plan_trat      # Asigna la FK manualmente
                nueva_sesion.save()                            # Guarda en la base de datos
                messages.success(request, "Sesión agregada al plan de tratamiento.")
                return redirect('tratamiento')
            else:
                for field, errors in formSesion.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en {field}: {error}")

        elif accion=="agendarCita": 
            #Id´s necesarios para agendar la cita correctamente
            sesion_id = request.POST.get('sesion_id')
            plan_tratamiento_id = request.POST.get('tratamiento_id')
            paciente_id=request.POST.get('paciente_id')

            datos_formulario = request.POST.copy()
            datos_formulario['paciente'] = paciente_id

            if not datos_formulario.get('tipo_cita'):
                datos_formulario['tipo_cita'] = 1

            
            formCita=FormCita(datos_formulario)
            
            if formCita.is_valid():
                nueva_cita=formCita.save(commit=False)
                nueva_cita.paciente_id=paciente_id
                nueva_cita.save()
                if sesion_id:
                    # Actualizar la sesión existente
                    nueva_cita.itemsesion_id = sesion_id
                    nueva_cita.save()
                    #Anteriormente era esto xd
                    # sesion = ItemSesion.objects.get(id=sesion_id)
                    # sesion.cita = nueva_cita
                    # sesion.save()
                    messages.success(request, "Cita agendada correctamente.")
                    return redirect('tratamiento')
                else: 
                #     #Creamos la sesión xd
                #     ItemSesion.objects.create(
                #         plan_tratamiento_id = plan_tratamiento_id,
                #         cita = nueva_cita
                #     )
                    messages.success(request, "No se encontró la sesión.")
                    return redirect('tratamiento')  
            else:
                for field, errors in formCita.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, f"{error}")
                        else:
                            messages.error(request, f"Error en {field}: {errors.as_text()}")

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
                    item = cita.itemsesion #ItemSesion.objects.filter(cita=cita).first()
                    if item:
                        plan = item.plan_tratamiento
                        plan.sesiones_realizadas += 1
                        plan.save()
                    
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

    dict_costoTratamiento = {tipo.id : float(tipo.precio_estimado) for tipo in TipoTratamiento.objects.all()}
    dict_precios_citas = {tipo.id : float(tipo.precio) for tipo in TipoCita.objects.all()}

    context = {
        'formTratamiento': formTratamiento,
        'formSesion': formSesion,
        'page_obj':page_obj,
        'q':q,
        'formCita':formCita,
        'precios_tratamientos_json': json.dumps(dict_costoTratamiento), #Enviamos los costos estimados
        'precios_citas_json': json.dumps(dict_precios_citas),
    }
    return render(request, 'tratamiento.html', context)

"""

                                            <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal"
                                                data-bs-target="#AgendarCitaModal{{ sesion.id }}">
                                                <i class="bi bi-plus"></i> Agendar
                                            </button>
"""