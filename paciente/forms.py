from django import forms
from .models import Paciente
from django.db.models import Q

class Formpaciente(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nb1', 'nb2', 'ap1', 'ap2', 'telefono', 'correo', 'sexo','cedula']

        labels = {
            'nb1': 'Primer Nombre',
            'nb2': 'Segundo Nombre',
            'ap1': 'Primer Apellido',
            'ap2': 'Segundo Apellido',
            'telefono': 'Teléfono',
            'correo': 'Correo Electrónico',
            'sexo': 'Sexo',
            'cedula': 'Cédula',
        }

        widgets = {
            'nb1': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-nb1',
            }),
            'nb2': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-nb2',
            }),
            'ap1': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-ap1',
            }),
            'ap2': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-ap2',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-telefono',
                'type': 'tel', 
                'maxlength': '8',
                'minlength': '8',
                'pattern': '[0-9]{8}',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '')"
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'input-correo',
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'input-sexo',
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'input-cedula',
            }),
        }
    def clean(self):
        cleaned_data = super().clean()
        
        nb1 = cleaned_data.get('nb1', '').strip()
        nb2 = cleaned_data.get('nb2', '')
        if nb2: nb2 = nb2.strip()
        
        ap1 = cleaned_data.get('ap1', '').strip()
        ap2 = cleaned_data.get('ap2', '')
        if ap2: ap2 = ap2.strip()
        
        telefono = cleaned_data.get('telefono')
        correo = cleaned_data.get('correo')

        query_nombre = Q(nb1__iexact=nb1) & Q(ap1__iexact=ap1)

        if nb2:
            query_nombre &= Q(nb2__iexact=nb2)
        else:
            query_nombre &= (Q(nb2__isnull=True) | Q(nb2=''))

        if ap2:
            query_nombre &= Q(ap2__iexact=ap2)
        else:
            query_nombre &= (Q(ap2__isnull=True) | Q(ap2=''))

        duplicado_nombre = Paciente.objects.filter(query_nombre)

        if self.instance.pk:
            duplicado_nombre = duplicado_nombre.exclude(pk=self.instance.pk)

        if duplicado_nombre.exists():
            raise forms.ValidationError(
                f"Ya existe un paciente registrado como '{nb1} {ap1}'. Verifica en el buscador."
            )
        
        if telefono:
            duplicado_tel = Paciente.objects.filter(telefono=telefono)
            if self.instance.pk:
                duplicado_tel = duplicado_tel.exclude(pk=self.instance.pk)
            
            if duplicado_tel.exists():
                self.add_error('telefono', f"El teléfono {telefono} ya pertenece a otro paciente.")

        if correo:
            duplicado_mail = Paciente.objects.filter(correo=correo)
            if self.instance.pk:
                duplicado_mail = duplicado_mail.exclude(pk=self.instance.pk)
            
            if duplicado_mail.exists():
                self.add_error('correo', f"El correo {correo} ya está registrado.")

        return cleaned_data
    
    def clean_cedula(self):
        if cedula := self.cleaned_data.get('cedula'):
            cedula = self.cleaned_data.get('cedula', '').upper()
            
            cedula_limpia = cedula.replace('-', '').replace(' ', '')

            if len(cedula_limpia) != 14:
                raise forms.ValidationError("La cédula debe tener 14 caracteres (13 números y 1 letra).")

            numeros = cedula_limpia[:13]
            letra = cedula_limpia[13]

            if not numeros.isdigit():
                raise forms.ValidationError("Los primeros 13 caracteres deben ser números.")
            
            if not letra.isalpha():
                raise forms.ValidationError("El último carácter debe ser una letra.")

            existe = Paciente.objects.filter(cedula=cedula_limpia)
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
                
            if existe.exists():
                raise forms.ValidationError("Esta cédula ya está registrada en el sistema.")

            return cedula_limpia