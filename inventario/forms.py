from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Categoria, Venta, DetalleVenta, Cliente


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'stock_inicial', 'stock_actual', 'precio', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: COCA DE 600',
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'stock_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
            }),
            'stock_actual': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.50',
                'placeholder': '0.00',
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del producto',
            'categoria': 'Categoría',
            'stock_inicial': 'Stock inicial',
            'stock_actual': 'Stock actual',
            'precio': 'Precio de venta ($)',
            'activo': 'Producto activo',
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Botanas'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción opcional'}),
        }


class AjusteStockForm(forms.Form):
    TIPO_CHOICES = [
        ('entrada', '📦 Entrada (restock)'),
        ('salida', '📤 Salida manual'),
        ('ajuste', '✏️ Ajuste directo'),
    ]
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo de ajuste'
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        label='Cantidad'
    )
    motivo = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
        label='Motivo'
    )


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['fecha', 'cliente', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente (opcional)'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notas opcionales'}),
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select producto-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control precio-unitario',
                'min': '0', 'step': '0.50',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True, stock_actual__gt=0).order_by('nombre')
        self.fields['producto'].empty_label = '— Selecciona un producto —'


DetalleVentaFormSet = inlineformset_factory(
    Venta, DetalleVenta,
    form=DetalleVentaForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas opcionales'
            }),
        }
        labels = {
            'nombre': 'Nombre',
            'notas': 'Notas',
        }


class AgregarProductoClienteForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        label='Fecha',
        required=False,
    )

    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0', 'step': '0.50'
            }),
        }
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio unitario ($)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(
        activo=True).order_by('nombre')
        self.fields['producto'].empty_label = '— Selecciona un producto —'


ClienteDetalleFormSet = inlineformset_factory(
    Venta, DetalleVenta,
    form=AgregarProductoClienteForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)