from django.db import models
from django.utils import timezone
from django.db.models import Sum


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Categoría")
    descripcion = models.CharField(max_length=255, blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Cliente")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    notas = models.TextField(blank=True, verbose_name="Notas")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    bloqueado = models.BooleanField(default=False, verbose_name="Bloqueado")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def deuda_total(self):
        return self.cuentas.filter(pagado=False).aggregate(
            t=Sum('total'))['t'] or 0

    @property
    def estado(self):
        if self.bloqueado:
            return 'bloqueado'
        return 'activo'

    @property
    def estado_badge(self):
        if self.bloqueado:
            return 'danger'
        return 'success'

    @property
    def estado_texto(self):
        if self.bloqueado:
            return '⛔ Bloqueado — No pagó'
        return '✅ Activo'


class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Producto")
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Categoría", related_name='productos'
    )
    stock_inicial = models.PositiveIntegerField(default=0, verbose_name="Stock inicial")
    stock_actual = models.IntegerField(default=0, verbose_name="Stock actual")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de venta ($)")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def semaforo(self):
        if self.stock_actual <= 0:
            return 'rojo'
        elif self.stock_actual <= 3:
            return 'naranja'
        else:
            return 'verde'

    @property
    def semaforo_badge(self):
        colores = {'rojo': 'danger', 'naranja': 'warning', 'verde': 'success'}
        return colores[self.semaforo]

    @property
    def semaforo_icon(self):
        iconos = {'rojo': '🔴', 'naranja': '🟠', 'verde': '🟢'}
        return iconos[self.semaforo]

    @property
    def semaforo_texto(self):
        textos = {'rojo': 'Agotado', 'naranja': 'Stock bajo', 'verde': 'Disponible'}
        return textos[self.semaforo]


class Venta(models.Model):
    fecha = models.DateField(default=timezone.now, verbose_name="Fecha")
    cliente = models.CharField(max_length=200, blank=True, verbose_name="Cliente")
    cliente_fk = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cuentas', verbose_name="Cliente (cuenta)"
    )
    pagado = models.BooleanField(default=True, verbose_name="Pagado")
    notas = models.TextField(blank=True, verbose_name="Notas")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")
    fecha_venta = models.DateField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha', '-creado_en']

    def __str__(self):
        cliente = self.cliente or 'Sin nombre'
        return f"Venta #{self.pk} - {cliente} - {self.fecha}"

    def calcular_total(self):
        total = sum(d.subtotal for d in self.detalles.all())
        self.total = total
        self.save(update_fields=['total'])
        return total


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario