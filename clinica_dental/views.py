from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def index(request):
    #return render(request, "paciente.html")
    return render(request, "templates/base.html")
