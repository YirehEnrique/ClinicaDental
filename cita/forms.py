from datetime import datetime, timedelta
from django.utils import timezone
from django import forms
from .models import Cita


class FormCita(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'hora', 'notas', 'paciente', 'dentista', 'tipo_cita', 'estado_cita', 'precio_cita']
        labels = {
            'fecha': 'Fecha de la Cita',
            'hora': 'Hora de la Cita',
            'notas': 'Notas Adicionales',
            'paciente': 'Paciente',
            'dentista': 'Dentista',
            'tipo_cita': 'Tipo de Cita',
            'estado_cita': 'Estado de la Cita',
            'precio_cita': 'Precio de la Cita',
        }

        widgets = {
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'hora': forms.TimeInput(attrs={
                'class': 'form-control anchura',
                'type': 'time',
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'paciente': forms.Select(attrs={
                'class': 'form-select',
            }),
            'dentista': forms.Select(attrs={
                'class': 'form-select',
            }),
            'tipo_cita': forms.Select(attrs={
                'class': 'form-select',
            }),
            'estado_cita': forms.Select(attrs={
                'class': 'form-control',
                'step': '0.10',
                'min': '0',
                'placeholder': '0.00'
            }),
            'precio_cita': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['precio_cita'].widget.attrs['readonly'] = True

        self.fields['estado_cita'].required = False
        self.fields['estado_cita'].initial = 1
        self.fields['fecha'].initial = timezone.now().date()
        self.fields['dentista'].empty_label = None

        self.fields['dentista'].queryset = self.fields['dentista'].queryset.filter(estado=True)

    def save(self, commit=True):
        obj = super().save(commit=False)

        #Esto sería para cuando se registra nueva cita
        if not obj.precio_cita or obj.precio_cita == 0:
            tipoC = self.cleaned_data.get('tipo_cita')
            if tipoC:
                obj.precio_cita = tipoC.precio 

        if self.cleaned_data.get('estado_cita') is None:
            obj.estado_cita_id = 1 
        if commit:
            obj.save()
        return obj
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        paciente = cleaned_data.get('paciente')

        #Validamos que el paciente no tenga citas agendadas previamente (pendientes)
        #Si hay un paciente que pasó validaciones 
        if paciente: 
            #Filtramos para obtener las citas pendientes del paciente (si las hay)
            citas_existentes = Cita.objects.filter(
                paciente = paciente,
                estado_cita = 1
            )

            #Si estamos editando un cita que ya existe (porque ya está en pendiente otra cita)
            if self.instance.pk:
                #Entonces excluimos la misma cita que estamos editando xd
                citas_existentes = citas_existentes.exclude(pk=self.instance.pk)
            
            #Si si hay conflcitos entonces devolvemos el error.
            if citas_existentes.exists():
                self.add_error('paciente', "El paciente ya tiene una cita agendada.")
                return cleaned_data

        #Validamos fecha y hora para agendar la cita
        if fecha and hora:
            cita_nueva_dt = datetime.combine(fecha, hora)

            #Rango límite para agendar las citas (40m)
            limite_inferior = (cita_nueva_dt - timedelta(minutes=39)).time()
            limite_superior = (cita_nueva_dt + timedelta(minutes=39)).time()

            #Comprobamos si existe algún conflicto
            citas_conflicto = Cita.objects.filter(
                fecha=fecha,
                hora__range=(limite_inferior, limite_superior)
            ).exclude(estado_cita_id=3)

            if self.instance.pk:
                citas_conflicto = citas_conflicto.exclude(pk=self.instance.pk)

            if citas_conflicto.exists():
                cita_ocupada = citas_conflicto.first() 
                mensaje = f"Choque de horario: Ya existe una cita a las {cita_ocupada.hora.strftime('%H:%M')}."
                self.add_error('hora', mensaje)

        return cleaned_data