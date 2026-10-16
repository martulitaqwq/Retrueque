from django import forms
from .models import Publicacion

class PublicacionForm(forms.ModelForm):
    # Hacemos que la descripción no bloquee el guardado si se deja vacía o con poco texto
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4,
            'placeholder': 'Cuenta detalles: marca, medidas, tiempo de uso, qué buscas a cambio...'
        }), 
        required=False
    )

class Meta:
        model = Publicacion
        fields = ['titulo', 'descripcion', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control campo-titulo', 
                'placeholder': 'Título del artículo'
            }),
            'categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría'
            }),
        }