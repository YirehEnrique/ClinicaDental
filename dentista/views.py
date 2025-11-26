from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import FormDentista
from .models import Dentista
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages 

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