from django.utils import timezone
from django import forms
from .models import PlanTratamiento, ItemSesion, TipoTratamiento #,PlanItems


class FormPlanTratamiento(forms.ModelForm):
    class Meta:
        model = PlanTratamiento
        fields = ['notas', 'estado', 'dentista', 'paciente', 'tratamiento','precio_estimado']

        #Declaramos los label que iran a los templates.
        labels = {
            'notas': 'Notas Adicionales',
            'estado': 'Estado',
            'dentista': 'Dentista',
            'paciente': 'Paciente',
            'tratamiento': 'Tipo de Tratamiento',
            'precio_estimado': 'Precio Estimado'
        }

        #Definimos los widgets y su tipo en dependencia de los datos a requerir y demás
        widgets = {
            'tratamiento': forms.Select(attrs={'class': 'form-select'}),
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'dentista': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'precio_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.10',
                'min': '0',
                'placeholder': '0.00'
            })
        }  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['precio_estimado'].widget.attrs['readonly'] = True

        self.fields['estado'].required = False
        self.fields['estado'].initial = 'E'
        self.fields['dentista'].queryset = self.fields['dentista'].queryset.filter(estado=True)

    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')
        tipo_tratamiento = cleaned_data.get('tratamiento')

        #Confirmamos si hay paciente y el tipo de tratamiento
        if paciente and tipo_tratamiento:
            #Excluimos los estados de cancelado y terminado de los tratamientos.
            duplicados = PlanTratamiento.objects.filter(
                paciente=paciente,
                tratamiento=tipo_tratamiento
            ).exclude(estado__in=['C', 'T'])

            #Confirmamos duplicados y los excluimos
            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)

            #Comprobamos que no hayan tratamientos duplicados y mandamos un mensaje xd
            if duplicados.exists():
                self.add_error('tratamiento', f"El paciente {paciente} ya tiene un tratamiento de '{tipo_tratamiento}' en curso.")
        #Retornamos los datos limpios 
        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=False)

        if not obj.precio_estimado or obj.precio_estimado == 0:
            tipoTC = self.cleaned_data.get('tratamiento')
            if tipoTC:
                obj.precio_estimado = tipoTC.precio_estimado 

        if commit:
            obj.save()
        return obj

class FormItemSesion(forms.ModelForm):
    class Meta:
        model = ItemSesion
        fields = ['nombre_sesion']  # Incluimos explícitamente el campo de nombre
        labels = {
            'nombre_sesion': 'Nombre de la sesión',
        }
        widgets = {
            'nombre_sesion': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }