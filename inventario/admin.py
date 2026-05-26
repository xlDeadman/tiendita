from django.contrib import admin
from .models import Producto, Categoria, Venta, DetalleVenta


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'stock_actual', 'precio', 'activo']
    list_filter = ['activo', 'categoria']
    search_fields = ['nombre']
    list_editable = ['precio', 'stock_actual', 'activo']


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['subtotal']

    def subtotal(self, obj):
        return f'${obj.subtotal:.2f}'


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha', 'total']
    list_filter = ['fecha']
    search_fields = ['cliente']
    inlines = [DetalleVentaInline]
