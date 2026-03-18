from django.contrib import admin
from tratamientos.models import ItemSesion, PlanTratamiento, TipoTratamiento, PlanItems

# Register your models here.
admin.site.register(ItemSesion)
admin.site.register(PlanTratamiento)
admin.site.register(TipoTratamiento)
admin.site.register(PlanItems)