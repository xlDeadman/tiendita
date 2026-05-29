from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('productos/', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/editar/', views.producto_edit, name='producto_edit'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    path('productos/<int:pk>/stock/', views.producto_ajuste_stock, name='producto_ajuste_stock'),

    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_edit, name='categoria_edit'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),

    path('egresos/', views.egreso_list, name='egreso_list'),
    path('egresos/nuevo/', views.egreso_create, name='egreso_create'),
    path('egresos/<int:pk>/eliminar/', views.egreso_delete, name='egreso_delete'),
    path('egresos/<int:pk>/editar/', views.egreso_edit, name='egreso_edit'),

    path('estado-cuenta/', views.estado_cuenta, name='estado_cuenta'),

    path('ventas/', views.venta_list, name='venta_list'),
    path('ventas/nueva/', views.venta_create, name='venta_create'),
    path('ventas/<int:pk>/', views.venta_detail, name='venta_detail'),
    path('ventas/<int:pk>/eliminar/', views.venta_delete, name='venta_delete'),

    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('clientes/<int:pk>/agregar/', views.cliente_agregar_producto, name='cliente_agregar_producto'),
    path('clientes/<int:pk>/pagar/', views.cliente_pagar, name='cliente_pagar'),
    path('clientes/<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    path('clientes/<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),
    path('clientes/<int:pk>/bloquear/', views.cliente_bloquear, name='cliente_bloquear'),
    path('clientes/<int:pk>/desbloquear/', views.cliente_desbloquear, name='cliente_desbloquear'),
    path('clientes/<int:cliente_pk>/detalle/<int:pk>/editar/', views.cliente_detalle_edit, name='cliente_detalle_edit'),
    path('clientes/<int:cliente_pk>/detalle/<int:pk>/eliminar/', views.cliente_detalle_delete, name='cliente_detalle_delete'),
    path('clientes/<int:pk>/abonar/', views.cliente_abonar, name='cliente_abonar'),

    path('api/producto/<int:pk>/precio/', views.api_precio_producto, name='api_precio_producto'),
    path('catalogo/', views.catalogo, name='catalogo'),
]