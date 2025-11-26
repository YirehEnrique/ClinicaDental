from django import forms
from .models import Dentista
from django.db.models import Q

class FormDentista(forms.ModelForm):
    class Meta:
        model = Dentista
        fields = ['nb1', 'nb2', 'ap1', 'ap2', 'telefono', 'correo', 'sexo']

        labels = {
            'nb1': 'Primer Nombre',
            'nb2': 'Segundo Nombre',
            'ap1': 'Primer Apellido',
            'ap2': 'Segundo Apellido',
            'telefono': 'Teléfono',
            'correo': 'Correo Electrónico',
            'sexo': 'Sexo',
        }

        widgets = {
            'nb1': forms.TextInput(attrs={'class': 'form-control', 'id': 'input-nb1'}),
            'nb2': forms.TextInput(attrs={'class': 'form-control', 'id': 'input-nb2'}),
            'ap1': forms.TextInput(attrs={'class': 'form-control', 'id': 'input-ap1'}),
            'ap2': forms.TextInput(attrs={'class': 'form-control', 'id': 'input-ap2'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-telefono',
                'type': 'tel',
                'maxlength': '8',
                'minlength': '8',
                'pattern': '[0-9]{8}',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '')"
            }),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'id': 'input-correo'}),
            'sexo': forms.Select(attrs={'class': 'form-select', 'id': 'input-sexo'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        nb1 = cleaned_data.get('nb1')
        nb2 = cleaned_data.get('nb2')
        ap1 = cleaned_data.get('ap1')
        ap2 = cleaned_data.get('ap2')
        telefono = cleaned_data.get('telefono')
        correo = cleaned_data.get('correo')

        if telefono:
            duplicado_tel = Dentista.objects.filter(telefono=telefono)
            if self.instance.pk:
                duplicado_tel = duplicado_tel.exclude(pk=self.instance.pk)
            
            if duplicado_tel.exists():
                self.add_error('telefono', f"El teléfono {telefono} ya está registrado con otro dentista.")

        if correo:
            duplicado_mail = Dentista.objects.filter(correo=correo)
            if self.instance.pk:
                duplicado_mail = duplicado_mail.exclude(pk=self.instance.pk)
            
            if duplicado_mail.exists():
                self.add_error('correo', f"El correo {correo} ya pertenece a otro dentista.")

        query_nombre = Q(nb1__iexact=nb1) & Q(ap1__iexact=ap1)

        if nb2:
            query_nombre &= Q(nb2__iexact=nb2)
        else:
            query_nombre &= (Q(nb2__isnull=True) | Q(nb2=''))

        if ap2:
            query_nombre &= Q(ap2__iexact=ap2)
        else:
            query_nombre &= (Q(ap2__isnull=True) | Q(ap2=''))

        duplicado_nombre = Dentista.objects.filter(query_nombre)

        if self.instance.pk:
            duplicado_nombre = duplicado_nombre.exclude(pk=self.instance.pk)

        if duplicado_nombre.exists():
            raise forms.ValidationError(
                f"Ya existe un dentista registrado como '{nb1} {ap1}'. Verifique en el buscador."
            )

        return cleaned_data