from django.db import models
from paciente.models import Paciente
from cita.models import Cita
from dentista.models import Dentista
# Create your models here.

class TipoTratamiento(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class PlanTratamiento(models.Model):
    tratamiento=models.ForeignKey(TipoTratamiento,  default=1,on_delete=models.CASCADE)
    paciente=models.ForeignKey(Paciente, default=1,
                            on_delete=models.CASCADE)
    dentista=models.ForeignKey(Dentista, default=1,
                            on_delete=models.CASCADE)
    #complejidad=models.CharField(max_length=1, 
    #                        choices=[('B','Baja'),('M','Media'),('A','Alta')], default='B')
    notas=models.TextField(blank=True, null=True)
    estado=models.CharField(max_length=1, 
                            choices=[('C','Cancelado'),('E','En Proceso'),('T','Completado')], default='E')
    creada=models.DateTimeField(auto_now_add=True)
    actualizada=models.DateTimeField(auto_now=True, blank=True, null=True)
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class PlanItems(models.Model):
    nombre=models.CharField(max_length=100, default='')
    plan_tratamiento=models.ForeignKey(PlanTratamiento, default=1, related_name='plan_items',
                            on_delete=models.CASCADE)
    orden=models.IntegerField(default=0)
    notas=models.TextField(blank=True, null=True)
    estado=models.CharField(max_length=1, 
    choices=[('P','Pendiente'),('E','En Proceso'),('C','Completado')], default='P')
    creada=models.DateTimeField(auto_now_add=True)
    actualizada=models.DateTimeField(auto_now=True, blank=True, null=True)

class ItemSesion(models.Model):
    plan_item=models.ForeignKey(PlanItems, default=1,
    on_delete=models.CASCADE)
    cita=models.ForeignKey(Cita, default=1,
                            on_delete=models.CASCADE)
    creada=models.DateTimeField(auto_now_add=True)
    actualizada=models.DateTimeField(auto_now=True, blank=True, null=True)