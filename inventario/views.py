from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from decimal import Decimal

from .models import Producto, Categoria, Venta, DetalleVenta, Cliente, Egreso, SaldoCaja
from .forms import (
    ProductoForm, CategoriaForm, AjusteStockForm,
    VentaForm, DetalleVentaFormSet, ClienteForm,
    AgregarProductoClienteForm, ClienteDetalleFormSet
)


# ─────────────────────────── Dashboard ───────────────────────────

@login_required
def dashboard(request):
    productos = Producto.objects.filter(activo=True)
    total_productos = productos.count()
    agotados = productos.filter(stock_actual__lte=0).count()
    stock_bajo = productos.filter(stock_actual__gt=0, stock_actual__lte=3).count()
    disponibles = productos.filter(stock_actual__gt=3).count()

    hoy = date.today()

    ventas_hoy = Venta.objects.filter(fecha=hoy, cliente_fk__isnull=True)
    total_hoy = ventas_hoy.aggregate(t=Sum('total'))['t'] or 0
    num_ventas_hoy = ventas_hoy.count()

    total_mes = Venta.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).aggregate(t=Sum('total'))['t'] or 0

    cobrado_mes = Venta.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month,
        cliente_fk__isnull=False,
        pagado=True
    ).aggregate(t=Sum('total'))['t'] or 0

    credito_mes = Venta.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month,
        cliente_fk__isnull=False
    ).aggregate(t=Sum('total'))['t'] or 0

    por_cobrar = credito_mes - cobrado_mes

    top_productos = (
        DetalleVenta.objects
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    productos_criticos = productos.filter(stock_actual__lte=3).order_by('stock_actual', 'nombre')[:50]
    ultimas_ventas = Venta.objects.order_by('-fecha', '-creado_en')[:5]

    context = {
        'total_productos': total_productos,
        'agotados': agotados,
        'stock_bajo': stock_bajo,
        'disponibles': disponibles,
        'total_hoy': total_hoy,
        'num_ventas_hoy': num_ventas_hoy,
        'total_mes': total_mes,
        'por_cobrar': por_cobrar,
        'top_productos': top_productos,
        'productos_criticos': productos_criticos,
        'ultimas_ventas': ultimas_ventas,
    }
    return render(request, 'inventario/dashboard.html', context)


# ─────────────────────────── Productos ───────────────────────────

@login_required
def producto_list(request):
    q = request.GET.get('q', '')
    semaforo = request.GET.get('semaforo', '')
    categoria_id = request.GET.get('categoria', '')
    mostrar_inactivos = request.GET.get('inactivos', '')

    productos = Producto.objects.select_related('categoria').all()

    if not mostrar_inactivos:
        productos = productos.filter(activo=True)
    if q:
        productos = productos.filter(nombre__icontains=q)
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if semaforo == 'rojo':
        productos = productos.filter(stock_actual__lte=0)
    elif semaforo == 'naranja':
        productos = productos.filter(stock_actual__gt=0, stock_actual__lte=3)
    elif semaforo == 'verde':
        productos = productos.filter(stock_actual__gt=3)

    categorias = Categoria.objects.all()
    context = {
        'productos': productos,
        'categorias': categorias,
        'q': q,
        'semaforo': semaforo,
        'categoria_id': categoria_id,
        'mostrar_inactivos': mostrar_inactivos,
    }
    return render(request, 'inventario/producto_list.html', context)


@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'✅ Producto "{producto.nombre}" creado correctamente.')
            return redirect('producto_list')
    else:
        form = ProductoForm()
    return render(request, 'inventario/producto_form.html', {
        'form': form, 'titulo': 'Nuevo producto', 'boton': 'Guardar producto',
    })


@login_required
def producto_edit(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Producto "{producto.nombre}" actualizado.')
            return redirect('producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/producto_form.html', {
        'form': form, 'producto': producto,
        'titulo': f'Editar: {producto.nombre}', 'boton': 'Guardar cambios',
    })


@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        if producto.detalles_venta.exists():
            producto.activo = False
            producto.save()
            messages.warning(request, f'⚠️ "{nombre}" tiene ventas registradas. Se desactivó en lugar de eliminar.')
        else:
            producto.delete()
            messages.success(request, f'🗑️ Producto "{nombre}" eliminado.')
        return redirect('producto_list')
    return render(request, 'inventario/producto_confirm_delete.html', {'producto': producto})


@login_required
def producto_ajuste_stock(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = AjusteStockForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']
            if tipo == 'entrada':
                producto.stock_actual += cantidad
                msg = f'📦 +{cantidad} unidades agregadas a "{producto.nombre}".'
            elif tipo == 'salida':
                producto.stock_actual = max(0, producto.stock_actual - cantidad)
                msg = f'📤 -{cantidad} unidades descontadas de "{producto.nombre}".'
            else:
                producto.stock_actual = cantidad
                msg = f'✏️ Stock de "{producto.nombre}" ajustado a {cantidad}.'
            producto.save()
            messages.success(request, msg)
            return redirect('producto_list')
    else:
        form = AjusteStockForm()
    return render(request, 'inventario/producto_ajuste_stock.html', {
        'form': form, 'producto': producto,
    })


# ─────────────────────────── Categorías ───────────────────────────

@login_required
def categoria_list(request):
    categorias = Categoria.objects.annotate(num_productos=Count('productos'))
    return render(request, 'inventario/categoria_list.html', {'categorias': categorias})


@login_required
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Categoría creada.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm()
    return render(request, 'inventario/categoria_form.html', {
        'form': form, 'titulo': 'Nueva categoría', 'boton': 'Guardar'
    })


@login_required
def categoria_edit(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Categoría actualizada.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'inventario/categoria_form.html', {
        'form': form, 'titulo': f'Editar: {categoria.nombre}', 'boton': 'Guardar cambios'
    })


@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'🗑️ Categoría "{nombre}" eliminada.')
        return redirect('categoria_list')
    return render(request, 'inventario/categoria_confirm_delete.html', {'categoria': categoria})


# ─────────────────────────── Ventas ───────────────────────────

@login_required
def venta_list(request):
    ventas = Venta.objects.prefetch_related('detalles__producto').order_by('-fecha', '-creado_en')
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    if fecha_desde:
        ventas = ventas.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha__lte=fecha_hasta)
    total_general = ventas.aggregate(t=Sum('total'))['t'] or 0
    context = {
        'ventas': ventas,
        'total_general': total_general,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    return render(request, 'inventario/venta_list.html', context)


@login_required
def venta_create(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            venta = form.save(commit=False)
            venta.total = 0
            venta.save()
            detalles = formset.save(commit=False)
            total = 0
            errores = []
            for detalle in detalles:
                detalle.venta = venta
                producto = detalle.producto
                if detalle.cantidad > producto.stock_actual:
                    errores.append(f'Stock insuficiente para {producto.nombre} (disponible: {producto.stock_actual})')
                else:
                    detalle.precio_unitario = detalle.precio_unitario or producto.precio
                    detalle.save()
                    producto.stock_actual -= detalle.cantidad
                    producto.save()
                    total += detalle.subtotal
            if errores:
                for e in errores:
                    messages.error(request, f'❌ {e}')
                venta.delete()
                return render(request, 'inventario/venta_form.html', {
                    'form': form, 'formset': formset, 'titulo': 'Nueva venta'
                })
            venta.total = total
            venta.save()
            messages.success(request, f'✅ Venta registrada. Total: ${total:.2f}')
            return redirect('venta_list')
    else:
        form = VentaForm(initial={'fecha': date.today()})
        formset = DetalleVentaFormSet()
    return render(request, 'inventario/venta_form.html', {
        'form': form, 'formset': formset, 'titulo': 'Registrar venta',
    })


@login_required
def venta_detail(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.select_related('producto').all()
    return render(request, 'inventario/venta_detail.html', {
        'venta': venta, 'detalles': detalles,
    })


@login_required
def venta_delete(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        for detalle in venta.detalles.all():
            detalle.producto.stock_actual += detalle.cantidad
            detalle.producto.save()
        venta.delete()
        messages.success(request, '🗑️ Venta eliminada. Stock restaurado.')
        return redirect('venta_list')
    return render(request, 'inventario/venta_confirm_delete.html', {'venta': venta})


# ─────────────────────────── API helper ───────────────────────────

@login_required
def api_precio_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return JsonResponse({
        'precio': str(producto.precio),
        'stock': producto.stock_actual,
        'nombre': producto.nombre,
    })


# ─────────────────────────── Clientes ───────────────────────────

@login_required
def cliente_list(request):
    clientes = Cliente.objects.filter(activo=True).annotate(
        deuda=Sum('cuentas__total', filter=Q(cuentas__pagado=False))
    )
    return render(request, 'inventario/cliente_list.html', {'clientes': clientes})


@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'✅ Cliente "{cliente.nombre}" creado. Ahora agrega sus productos.')
            return redirect('cliente_agregar_producto', pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, 'inventario/cliente_form.html', {
        'form': form, 'titulo': 'Nuevo cliente',
    })


@login_required
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cuentas = cliente.cuentas.prefetch_related('detalles__producto').order_by('-fecha')
    deuda_total = cuentas.filter(pagado=False).aggregate(t=Sum('total'))['t'] or 0
    return render(request, 'inventario/cliente_detail.html', {
        'cliente': cliente, 'cuentas': cuentas, 'deuda_total': deuda_total,
    })


@login_required
def cliente_agregar_producto(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if cliente.bloqueado:
        messages.error(request, f'⛔ {cliente.nombre} está bloqueado. No se pueden agregar productos.')
        return redirect('cliente_detail', pk=pk)
    if request.method == 'POST':
        form = AgregarProductoClienteForm(request.POST)
        if form.is_valid():
            venta = Venta.objects.create(
                cliente_fk=cliente, pagado=False, total=0, fecha=date.today()
            )
            detalle = form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            producto = detalle.producto
            producto.stock_actual -= detalle.cantidad
            producto.save()
            venta.total = detalle.subtotal
            venta.save()
            messages.success(request, f'✅ Producto agregado a la cuenta de {cliente.nombre}.')
            return redirect('cliente_detail', pk=pk)
    else:
        form = AgregarProductoClienteForm()
    return render(request, 'inventario/cliente_agregar_producto.html', {
        'form': form, 'cliente': cliente
    })


@login_required
def cliente_pagar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.cuentas.all().delete()
        cliente.bloqueado = False
        cliente.save()
        messages.success(request, f'✅ Deuda de {cliente.nombre} saldada. Historial limpio.')
    return redirect('cliente_detail', pk=pk)


@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        nombre = cliente.nombre
        cliente.delete()
        messages.success(request, f'🗑️ Cliente "{nombre}" eliminado.')
        return redirect('cliente_list')
    return render(request, 'inventario/cliente_confirm_delete.html', {'cliente': cliente})


@login_required
def cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    detalles_pendientes = DetalleVenta.objects.filter(
        venta__cliente_fk=cliente,
        venta__pagado=False
    ).select_related('producto', 'venta')
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Cliente "{cliente.nombre}" actualizado.')
            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'inventario/cliente_edit.html', {
        'form': form,
        'cliente': cliente,
        'detalles_pendientes': detalles_pendientes,
        'titulo': f'Editar: {cliente.nombre}',
    })


@login_required
def cliente_detalle_edit(request, pk, cliente_pk):
    detalle = get_object_or_404(DetalleVenta, pk=pk)
    cliente = get_object_or_404(Cliente, pk=cliente_pk)
    cantidad_anterior = detalle.cantidad
    if request.method == 'POST':
        form = AgregarProductoClienteForm(request.POST, instance=detalle)
        if form.is_valid():
            detalle = form.save(commit=False)
            diferencia = detalle.cantidad - cantidad_anterior
            detalle.producto.stock_actual -= diferencia
            detalle.producto.save()
            detalle.save()
            fecha = form.cleaned_data.get('fecha')
            if fecha:
                detalle.venta.fecha = fecha
                detalle.venta.save()
            detalle.venta.calcular_total()
            messages.success(request, '✅ Producto actualizado.')
            return redirect('cliente_detail', pk=cliente_pk)
    else:
        form = AgregarProductoClienteForm(instance=detalle, initial={'fecha': detalle.venta.fecha})
    return render(request, 'inventario/cliente_agregar_producto.html', {
        'form': form, 'cliente': cliente, 'titulo': 'Editar producto'
    })


@login_required
def cliente_detalle_delete(request, pk, cliente_pk):
    detalle = get_object_or_404(DetalleVenta, pk=pk)
    cliente = get_object_or_404(Cliente, pk=cliente_pk)
    if request.method == 'POST':
        detalle.producto.stock_actual += detalle.cantidad
        detalle.producto.save()
        venta = detalle.venta
        detalle.delete()
        venta.calcular_total()
        messages.success(request, '🗑️ Producto eliminado de la cuenta.')
        return redirect('cliente_detail', pk=cliente_pk)
    return render(request, 'inventario/cliente_detalle_confirm_delete.html', {
        'detalle': detalle, 'cliente': cliente
    })


@login_required
def cliente_bloquear(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.bloqueado = True
        cliente.save()
        messages.warning(request, f'⛔ Cliente "{cliente.nombre}" bloqueado — No pagó.')
    return redirect('cliente_list')


@login_required
def cliente_desbloquear(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.bloqueado = False
        cliente.save()
        messages.success(request, f'✅ Cliente "{cliente.nombre}" desbloqueado.')
    return redirect('cliente_list')


@login_required
def cliente_abonar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            abono = Decimal(request.POST.get('abono', 0))
        except:
            messages.error(request, '❌ Cantidad inválida.')
            return redirect('cliente_detail', pk=pk)

        if abono <= 0:
            messages.error(request, '❌ El abono debe ser mayor a $0.')
            return redirect('cliente_detail', pk=pk)

        cuentas_pendientes = cliente.cuentas.filter(pagado=False).order_by('fecha')
        restante = abono

        for cuenta in cuentas_pendientes:
            if restante <= 0:
                break
            if restante >= cuenta.total:
                restante -= cuenta.total
                cuenta.pagado = True
                cuenta.save()
            else:
                cuenta.total -= restante
                cuenta.save()
                restante = Decimal(0)

        messages.success(request, f'✅ Abono de ${abono:.2f} registrado para {cliente.nombre}.')
    return redirect('cliente_detail', pk=pk)


# ─────────────────────────── Egresos ───────────────────────────

@login_required
def egreso_list(request):
    hoy = date.today()
    egresos = Egreso.objects.select_related('categoria').all()
    total_mes = egresos.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).aggregate(t=Sum('costo'))['t'] or 0
    categorias = Categoria.objects.all()
    saldo = SaldoCaja.get()
    return render(request, 'inventario/egreso_list.html', {
        'egresos': egresos,
        'total_mes': total_mes,
        'categorias': categorias,
        'saldo': saldo,
    })


@login_required
def egreso_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        categoria_id = request.POST.get('categoria') or None
        piezas = request.POST.get('piezas', 0)
        costo = request.POST.get('costo', 0)
        forma_pago = request.POST.get('forma_pago', 'efectivo')
        monto_efectivo = Decimal(request.POST.get('monto_efectivo', 0) or 0)
        monto_banco = Decimal(request.POST.get('monto_banco', 0) or 0)

        if nombre and piezas and costo:
            costo = Decimal(costo)

            # Si es efectivo o banco, el monto es el total
            if forma_pago == 'efectivo':
                monto_efectivo = costo
                monto_banco = Decimal(0)
            elif forma_pago == 'banco':
                monto_banco = costo
                monto_efectivo = Decimal(0)

            Egreso.objects.create(
                nombre=nombre,
                categoria_id=categoria_id,
                piezas=int(piezas),
                costo=costo,
                forma_pago=forma_pago,
                monto_efectivo=monto_efectivo,
                monto_banco=monto_banco,
            )

            # Descontar del saldo
            saldo = SaldoCaja.get()
            saldo.efectivo -= monto_efectivo
            saldo.banco -= monto_banco
            saldo.save()

            messages.success(request, f'✅ Egreso "{nombre}" registrado.')
        else:
            messages.error(request, '❌ Completa todos los campos.')
    return redirect('egreso_list')


@login_required
def egreso_delete(request, pk):
    egreso = get_object_or_404(Egreso, pk=pk)
    if request.method == 'POST':
        # Restaurar saldo al eliminar
        saldo = SaldoCaja.get()
        saldo.efectivo += egreso.monto_efectivo
        saldo.banco += egreso.monto_banco
        saldo.save()
        egreso.delete()
        messages.success(request, '🗑️ Egreso eliminado. Saldo restaurado.')
    return redirect('egreso_list')


# ─────────────────────────── Estado de cuenta ───────────────────────────

@login_required
def estado_cuenta(request):
    saldo = SaldoCaja.get()
    if request.method == 'POST':
        try:
            efectivo = Decimal(request.POST.get('efectivo', 0) or 0)
            banco = Decimal(request.POST.get('banco', 0) or 0)
            saldo.efectivo = efectivo
            saldo.banco = banco
            saldo.save()
            messages.success(request, '✅ Saldo actualizado correctamente.')
        except:
            messages.error(request, '❌ Valores inválidos.')
    return render(request, 'inventario/estado_cuenta.html', {'saldo': saldo})