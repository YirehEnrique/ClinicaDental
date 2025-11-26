from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class Paciente(models.Model):
    solo_numeros = RegexValidator(
        regex=r'^\d{8}$', 
        message='El teléfono debe contener solo números.',
        code='invalid_number'
    )

    nb1 = models.CharField(max_length=30)
    nb2 = models.CharField(max_length=30, blank=True, null=True)
    ap1 = models.CharField(max_length=30)
    ap2 = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=8, validators=[solo_numeros], blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    sexo=models.CharField(max_length=10, choices=[('M','Masculino'),('F','Femenino')])
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nb1} {self.ap1}"