from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.dentista, name='dentista'),
    path('perfil/', v.perfil_dentista, name='perfil_dentista'),
    path('cambio-contra/', v.cambio_contra, name='cambio_contra')
]