from django.utils import timezone
from django.db import models

from paciente.models import Paciente
from dentista.models import Dentista

# Create your models here.


class TipoCita(models.Model):
    tipo = models.CharField(max_length=50)

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
    estado_cita = models.ForeignKey(EstadoCita, default=1, on_delete=models.CASCADE)
    creada = models.DateTimeField(default=timezone.now)
    actualizada = models.DateTimeField(auto_now=True, blank=True, null=True)
