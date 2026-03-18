from django.contrib import admin
from cita.models import Cita, TipoCita, EstadoCita
# Register your models here.
admin.site.register(Cita)
admin.site.register(TipoCita)
@admin.register(EstadoCita)
class cita_Admin(admin.ModelAdmin):
    list_display = ('id', 'estado') 