from datetime import datetime, timedelta
from django.utils import timezone
from django import forms
from .models import Cita


class FormCita(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'hora', 'notas', 'paciente', 'dentista', 'tipo_cita', 'estado_cita']
        labels = {
            'fecha': 'Fecha de la Cita',
            'hora': 'Hora de la Cita',
            'notas': 'Notas Adicionales',
            'paciente': 'Paciente',
            'dentista': 'Dentista',
            'tipo_cita': 'Tipo de Cita',
            'estado_cita': 'Estado de la Cita',
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
                'class': 'form-select',
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado_cita'].required = False
        self.fields['estado_cita'].initial = 1
        self.fields['fecha'].initial = timezone.now().date()
        self.fields['dentista'].empty_label = None

        self.fields['dentista'].queryset = self.fields['dentista'].queryset.filter(estado=True)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.cleaned_data.get('estado_cita') is None:
            obj.estado_cita_id = 1 
        if commit:
            obj.save()
        return obj
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        
        if fecha and hora:
            cita_nueva_dt = datetime.combine(fecha, hora)

            limite_inferior = (cita_nueva_dt - timedelta(minutes=29)).time()
            limite_superior = (cita_nueva_dt + timedelta(minutes=29)).time()

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