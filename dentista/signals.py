from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Dentista
from datetime import datetime

User = get_user_model()

@receiver(post_save, sender=Dentista) 
def crear_usuario_para_dentista(sender, instance, created, **kwargs):
    
    if not created:
        return
    
    if instance.usuario:
        return
    
    username = instance.telefono or (instance.nb1 + '' + instance.ap1)
    if not username:
        return
    
    #La contraseña es nombres y/o apellidos todo en minúsculas
    partes = [
        instance.nb1 or '',
        instance.nb2 or '',
        instance.ap1 or '',
        instance.ap2 or '',
    ]
    #Si hay p (elemento del for ps), entonces lo pone en minúscula y lo agrega a la contraseña
    password = ''.join([p[0].lower() for p in partes if p])

    user = User.objects.create_user(
        username=username,
        password=password,
        rol="dentista",
        is_active=True,
        is_staff = False
    )
    instance.usuario = user
    instance.save(update_fields=['usuario'])