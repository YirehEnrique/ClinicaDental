from django import forms
from .models import Dentista
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm

class FormDentista(forms.ModelForm):
    class Meta:
        model = Dentista
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
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'id': 'input-cedula'}),
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
        cedula= cleaned_data.get('cedula')

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
        
        if cedula:
            duplicado_cedula = Dentista.objects.filter(cedula=cedula)
            if self.instance.pk:
                duplicado_cedula = duplicado_cedula.exclude(pk=self.instance.pk)
            
            if duplicado_cedula.exists():
                self.add_error('cedula', f"La cédula {cedula} ya está registrada con otro dentista.")

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
    def clean_cedula(self):
        # 1. Obtener el dato y convertir a mayúsculas
        cedula = self.cleaned_data.get('cedula', '').upper()
        
        # 2. Limpieza: Quitar guiones y espacios vacíos
        cedula_limpia = cedula.replace('-', '').replace(' ', '')

        # 3. Validación de Longitud (Deben quedar 14 caracteres exactos)
        if len(cedula_limpia) != 14:
            raise forms.ValidationError("La cédula debe tener 14 caracteres (13 números y 1 letra).")

        # 4. Validación de Estructura (13 números + 1 Letra)
        numeros = cedula_limpia[:13] # Los primeros 13
        letra = cedula_limpia[13]    # El último

        if not numeros.isdigit():
            raise forms.ValidationError("Los primeros 13 caracteres deben ser números.")
        
        if not letra.isalpha():
            raise forms.ValidationError("El último carácter debe ser una letra.")

        # 5. (Opcional) Validación de duplicados
        # Si quieres evitar que dos personas tengan la misma cédula
        existe = Dentista.objects.filter(cedula=cedula_limpia) # O usa Dentista.objects si es para dentistas
        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)
            
        if existe.exists():
            raise forms.ValidationError("Esta cédula ya está registrada en el sistema.")

        # Retornamos la cédula limpia (sin guiones) para que se guarde estandarizada
        return cedula_limpia
    

# class CustomPasswordChangeForm(PasswordChangeForm):
#     old_password = forms.CharField(
#         label="Contraseña actual",
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control'
#         })
#     )

#     new_password1 = forms.CharField(
#         label="Nueva contraseña",
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control'
#         })
#     )

#     new_password2 = forms.CharField(
#         label="Confirmar nueva contraseña",
#         widget=forms.PasswordInput(attrs={
#             'class': 'form-control'
#         })
#     )

# class CustomPasswordResetForm(PasswordResetForm):
#     email = forms.EmailField(
#         label="Correo electrónico",
#         widget=forms.EmailInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Ingrese su correo registrado'
#         })
#     )