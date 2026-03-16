from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django.utils import timezone

from clinica_dental import settings
# Create your models here.
"""
class UserManager(BaseUserManager):
    def _create_user(self, username, email,password, is_staff, is_superuser, **extrafields):
        user = self.model(
            username = username,
            email = email,
            is_staff = is_staff,
            is_superuser = is_superuser,
            **extrafields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user
    def create_user(self, username, email, name, last_name,password = None, **extrafields):
        return self._create_user(username, email, name, last_name,password, False, False, **extrafields)
    
    def create_superuser(self, username, email, name, last_name,password = None, **extrafields):
        return self._create_user(username, email, name, last_name,password, True, True, **extrafields)
    
class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True)
    email = models.EmailField('Correo Electrónico', max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    class Meta: 
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
    
    USERNAME_FIELD = 'username'
    #REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username

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
    telefono = models.CharField(max_length=8, validators=[solo_numeros], blank=False, null=False, default='00000000')
    correo = models.EmailField(blank=True, null=True)
    sexo=models.CharField(max_length=10, choices=[('M','Masculino'),('F','Femenino')])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    cedula=models.CharField(
        max_length=16,
        blank=True,
        null=True,
    )
    #fecha_nacimiento = models.DateTimeField(default= timezone.now(), blank=True)
    #es_menor = models.BooleanField(default=False)
    #usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nb1} {self.ap1}"
