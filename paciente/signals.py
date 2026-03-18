from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Paciente
from datetime import datetime

User = get_user_model()

@receiver(post_save, sender=Paciente) 
def crear_usuario_para_paciente(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.usuario:
        return
    if instance.es_menor:
        return
    
    username = instance.telefono
    if not username:
        return
    partes = [
        instance.nb1 or '',
        instance.nb2 or '',
        instance.ap1 or '',
        instance.ap2 or '',
    ]

    password = ''.join([p[0].lower() for p in partes if p])

    user = User.objects.create_user(
        username=username,
        password=password,
        #telefono=instance.telefono
    )
    instance.usuario = user
    instance.save(update_fields=['usuario'])