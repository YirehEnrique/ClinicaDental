from django.db import models
from django.conf import settings

# Create your models here. 
class Dentista(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    nb1 = models.CharField(max_length=30)
    nb2 = models.CharField(max_length=30, blank=True, null=True)
    ap1 = models.CharField(max_length=30)
    ap2 = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    sexo=models.CharField(max_length=10, choices=[('M','Masculino'),('F','Femenino')])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    cedula = models.CharField(max_length=16, unique=True, default='')
    estado=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nb1} {self.ap1}"