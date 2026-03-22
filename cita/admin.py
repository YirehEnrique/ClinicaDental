from django.contrib import admin
from cita.models import Cita, TipoCita, EstadoCita, PeticionCita
# Register your models here.
@admin.register(Cita)
class Pcita_Admin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'dentista', 'tipo_cita', 'precio_cita', 'estado_cita')

@admin.register(PeticionCita)
class Pcita_Admin(admin.ModelAdmin):
    list_display = ('id', 'paciente')

@admin.register(TipoCita)
class Tipocita_Admin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'precio') 

@admin.register(EstadoCita)
class Estadocita_Admin(admin.ModelAdmin):
    list_display = ('id', 'estado') 