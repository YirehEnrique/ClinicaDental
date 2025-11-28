from django.db import models

# Create your models here.
class Dentista(models.Model):
    nb1 = models.CharField(max_length=30)
    nb2 = models.CharField(max_length=30, blank=True, null=True)
    ap1 = models.CharField(max_length=30)
    ap2 = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    sexo=models.CharField(max_length=10, choices=[('M','Masculino'),('F','Femenino')])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nb1} {self.ap1}"