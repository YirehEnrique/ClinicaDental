from django.utils import timezone
from django.db import models
from datetime import datetime

from paciente.models import Paciente
from dentista.models import Dentista

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from tratamientos.models import PlanTratamiento

# Create your models here.

class TipoCita(models.Model):
    tipo = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.tipo
    
class EstadoCita(models.Model):
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.estado

class Cita(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    hora = models.TimeField(default="10:00")
    notas = models.TextField(blank=True, null=True)
    paciente = models.ForeignKey(Paciente,default=1, on_delete=models.CASCADE)
    dentista = models.ForeignKey(Dentista, default=1 ,on_delete=models.SET_NULL,null=True,blank=True)
    tipo_cita = models.ForeignKey(TipoCita,default=1, on_delete=models.CASCADE)
    precio_cita = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado_cita = models.ForeignKey(EstadoCita, default=1, on_delete=models.CASCADE)
    creada = models.DateTimeField(default=timezone.now)
    actualizada = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f'{self.tipo_cita}'#: {self.paciente.nb1} {self.paciente.ap1}'


class PeticionCita(models.Model):
    paciente = models.ForeignKey('paciente.Paciente', on_delete=models.CASCADE, default= 1)
    tratamiento = models.ForeignKey('tratamientos.PlanTratamiento', on_delete=models.CASCADE, default= 1)
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=timezone.now)
    estado_cita = models.ForeignKey('cita.EstadoCita', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}'