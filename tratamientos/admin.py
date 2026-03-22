from django.contrib import admin
from tratamientos.models import ItemSesion, PlanTratamiento, TipoTratamiento, PlanItems

# Register your models here.
#Creo que esta última se puede mejorar xd
@admin.register(ItemSesion)
class Itemsesion_Admin(admin.ModelAdmin):
    list_display = ('id', 'cita', 'plan_item')

@admin.register(TipoTratamiento)
class Ttratamiento_Admin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio_estimado')

@admin.register(PlanItems)
class tratamientoItem_Admin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'plan_tratamiento', 'estado') 

@admin.register(PlanTratamiento)
class Ptratamiento_Admin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'tratamiento') 