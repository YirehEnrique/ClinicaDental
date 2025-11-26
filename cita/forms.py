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
        # Que NO sea obligatorio en el formulario
        self.fields['estado_cita'].required = False
        # Que salga por defecto el estado con id 1 (ej. Pendiente)
        self.fields['estado_cita'].initial = 1
        # Inicio automatico con la fecha actual
        self.fields['fecha'].initial = timezone.now().date()

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Si el usuario no eligió nada, ponle estado 1
        if self.cleaned_data.get('estado_cita') is None:
            obj.estado_cita_id = 1   # o EstadoCita.objects.get(pk=1)
        if commit:
            obj.save()
        return obj