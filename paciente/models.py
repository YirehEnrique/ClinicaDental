from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, AbstractUser

#from django.utils import timezone
from clinica_dental import settings

# Create your models here.
class Usuario(AbstractUser):
    #telefono = models.CharField(max_length=8, null=True, blank=True)
    cuentas_permitidas = models.IntegerField(null=True, blank=True)

    class Meta: 
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
    
    def __str__(self):
        return self.username
"""
class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cuentas_permitidas = models.IntegerField(default=1)
    class Meta: 
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'
"""

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
    telefono = models.CharField(max_length=8, validators=[solo_numeros], blank=False, null=False)#, default='')
    correo = models.EmailField(blank=True, null=True)
    sexo=models.CharField(max_length=10, choices=[('M','Masculino'),('F','Femenino')])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    cedula=models.CharField(
        max_length=16,
        blank=True,
        null=True,
    )
    es_menor = models.BooleanField(default=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.nb1} {self.ap1}"