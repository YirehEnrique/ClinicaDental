from django.utils import timezone
from django import forms
from .models import PlanTratamiento, PlanItems, ItemSesion, TipoTratamiento


class FormPlanTratamiento(forms.ModelForm):
    class Meta:
        model = PlanTratamiento
        fields = ['complejidad', 'notas', 'estado', 'dentista', 'paciente', 'tratamiento']

        labels = {
            'complejidad': 'Nivel de Complejidad',
            'notas': 'Notas Adicionales',
            'estado': 'Estado',
            'dentista': 'Dentista',
            'paciente': 'Paciente',
            'tratamiento': 'Tipo de Tratamiento',
        }

        widgets = {
            'tratamiento': forms.Select(attrs={'class': 'form-select'}),
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'dentista': forms.Select(attrs={'class': 'form-select'}),
            'complejidad': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].required = False
        self.fields['estado'].initial = 'E'
        self.fields['dentista'].queryset = self.fields['dentista'].queryset.filter(estado=True)

    def clean(self):
        cleaned_data = super().clean()
        paciente = cleaned_data.get('paciente')
        tipo_tratamiento = cleaned_data.get('tratamiento')

        if paciente and tipo_tratamiento:
            duplicados = PlanTratamiento.objects.filter(
                paciente=paciente,
                tratamiento=tipo_tratamiento
            ).exclude(estado__in=['C', 'T'])

            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)

            if duplicados.exists():
                self.add_error('tratamiento', f"El paciente {paciente} ya tiene un tratamiento de '{tipo_tratamiento}' en curso.")
        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=False)
        if commit:
            obj.save()
        return obj


class FormPlanItems(forms.ModelForm):
    class Meta:
        model = PlanItems
        fields = ['nombre', 'orden', 'notas']
        labels = {
            'nombre': 'Nombre del Item',
            'orden': 'Orden del Item',
            'notas': 'Notas Adicionales',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'orden': forms.HiddenInput(),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }
    def __init__(self, *args, **kwargs):
        plan_tratamiento = kwargs.get('initial', {}).get('plan_tratamiento')

        super().__init__(*args, **kwargs)
        if plan_tratamiento:
            ultimo_plan_item = PlanItems.objects.filter(plan_tratamiento=plan_tratamiento).order_by('-orden').first()
           
            if ultimo_plan_item:
                self.fields['orden'].initial = ultimo_plan_item.orden + 1
            else:
                self.fields['orden'].initial = 1
        self.fields['orden'].required = False


class FormItemSesion(forms.ModelForm):
    class Meta:
        model = ItemSesion
        fields=['plan_item','cita']