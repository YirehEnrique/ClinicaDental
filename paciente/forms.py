from django import forms
from .models import Paciente  # asegúrate que sea el modelo correcto
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
                'type': 'tel',  # Muestra teclado numérico en celulares
                'maxlength': '8',
                'minlength': '8',
                'pattern': '[0-9]{8}', # Ayuda a validación HTML5
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
        
        # 1. OBTENER Y LIMPIAR DATOS (Quitamos espacios sobrantes con .strip())
        nb1 = cleaned_data.get('nb1', '').strip()
        nb2 = cleaned_data.get('nb2', '') # Si es None, lo dejamos como cadena vacía ''
        if nb2: nb2 = nb2.strip()
        
        ap1 = cleaned_data.get('ap1', '').strip()
        ap2 = cleaned_data.get('ap2', '')
        if ap2: ap2 = ap2.strip()
        
        telefono = cleaned_data.get('telefono')
        correo = cleaned_data.get('correo')

        # 2. VALIDAR DUPLICIDAD DE NOMBRE COMPLETO
        # Usamos __iexact para que "Juan" sea igual a "juan" o "JUAN"
        
        # Base de la consulta: Primer Nombre y Primer Apellido (Obligatorios)
        query_nombre = Q(nb1__iexact=nb1) & Q(ap1__iexact=ap1)

        # Validación del Segundo Nombre (Opcional)
        if nb2:
            # Si el usuario escribió un segundo nombre, buscamos coincidencia exacta
            query_nombre &= Q(nb2__iexact=nb2)
        else:
            # Si el usuario NO escribió segundo nombre, buscamos en la BD registros que TAMPOCO tengan
            query_nombre &= (Q(nb2__isnull=True) | Q(nb2=''))

        # Validación del Segundo Apellido (Opcional)
        if ap2:
            query_nombre &= Q(ap2__iexact=ap2)
        else:
            query_nombre &= (Q(ap2__isnull=True) | Q(ap2=''))

        # Ejecutamos la búsqueda
        duplicado_nombre = Paciente.objects.filter(query_nombre)

        # Excluir al propio paciente si estamos editando
        if self.instance.pk:
            duplicado_nombre = duplicado_nombre.exclude(pk=self.instance.pk)

        if duplicado_nombre.exists():
            raise forms.ValidationError(
                f"Ya existe un paciente registrado como '{nb1} {ap1}'. Verifica en el buscador."
            )

        # 3. VALIDAR TELÉFONO
        if telefono:
            duplicado_tel = Paciente.objects.filter(telefono=telefono)
            if self.instance.pk:
                duplicado_tel = duplicado_tel.exclude(pk=self.instance.pk)
            
            if duplicado_tel.exists():
                self.add_error('telefono', f"El teléfono {telefono} ya pertenece a otro paciente.")

        # 4. VALIDAR CORREO
        if correo:
            duplicado_mail = Paciente.objects.filter(correo=correo)
            if self.instance.pk:
                duplicado_mail = duplicado_mail.exclude(pk=self.instance.pk)
            
            if duplicado_mail.exists():
                self.add_error('correo', f"El correo {correo} ya está registrado.")

        return cleaned_data
    
    def clean_cedula(self):
        if cedula := self.cleaned_data.get('cedula'):
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
            existe = Paciente.objects.filter(cedula=cedula_limpia) # O usa Paciente.objects si es para pacientes
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
                
            if existe.exists():
                raise forms.ValidationError("Esta cédula ya está registrada en el sistema.")

            # Retornamos la cédula limpia (sin guiones) para que se guarde estandarizada
            return cedula_limpia