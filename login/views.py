from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages 

# Create your views here.  

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
        return redirect('cita')
    if request.method == 'POST':
        print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('cita')
        else:
            messages.error(request, 'Usuario o contraseña incorrecto')
            return render(request, 'login.html', {
                'title': 'Inicio de Sesión'
            })
    
    return render(request, 'login.html', {
        'title': 'Inicio de Sesión'
    })

def logout_view(request):
    logout(request)
    return redirect('login')