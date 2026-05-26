# 🏪 Tiendita — Sistema de Inventario

Sistema Django para control de inventario de tiendita de oficina.

## Stack

- Python 3.11+ / Django 5.0
- Bootstrap 5 + Bootstrap Icons
- PostgreSQL 17
- Conda (env manager)

---

## 🚀 Puesta en marcha

### 1. Crear la base de datos en PostgreSQL

```sql
-- Conectarte a psql y ejecutar:
CREATE DATABASE tiendita_db;
-- (si usas un usuario distinto a postgres, ajusta .env)
```

### 2. Crear entorno conda

```bash
conda create -n tiendita python=3.11 -y
conda activate tiendita
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tu password de PostgreSQL y demás datos
```

### 5. Correr migraciones

```bash
python manage.py migrate
```

### 6. Cargar los productos del Excel original

```bash
python manage.py cargar_productos
```

Esto crea las 4 categorías (Botanas, Bebidas, Dulces, Postres)
y los 30 productos con sus precios y stock iniciales.

### 7. Crear superusuario (para entrar al sistema)

```bash
python manage.py createsuperuser
```

### 8. Arrancar el servidor

```bash
python manage.py runserver
```

Abre http://127.0.0.1:8000 🎉

---

## 📋 Funcionalidades

| Módulo | Descripción |
|---|---|
| **Dashboard** | Resumen de stock, ventas del día/mes, semáforo, top productos |
| **Productos** | Alta, edición, eliminación, filtros, semáforo de stock |
| **Stock** | Ajuste por entrada / salida / ajuste directo |
| **Categorías** | CRUD simple (Botanas, Bebidas, etc.) |
| **Ventas** | Registro de ventas con múltiples productos, descuenta stock automáticamente |
| **Historial** | Listado filtrable por fecha, detalle por venta |

## 🚦 Semáforo de stock

| Color | Condición |
|---|---|
| 🔴 Rojo | 0 piezas — Agotado |
| 🟠 Naranja | 1–2 piezas — Stock bajo |
| 🟢 Verde | 3+ piezas — Disponible |

---

## 💡 Mejoras sugeridas (próximos pasos)

1. **Exportar a Excel** — Botón para descargar inventario/ventas como `.xlsx`
2. **Código de barras** — Campo opcional para escanear con lector
3. **Precio de costo** — Para calcular margen de ganancia
4. **Alertas por email** — Cuando un producto llega a stock bajo
5. **Múltiples usuarios** — Roles (admin vs cajero)
6. **Modo oscuro** — Ya está el sidebar oscuro, fácil de extender

---

## 📁 Estructura del proyecto

```
tiendita_project/
├── manage.py
├── requirements.txt
├── .env.example
├── tiendita_project/
│   ├── settings.py
│   └── urls.py
└── inventario/
    ├── models.py        ← Producto, Categoria, Venta, DetalleVenta
    ├── views.py         ← Toda la lógica
    ├── forms.py         ← Formularios
    ├── urls.py          ← Rutas
    ├── admin.py         ← Django admin
    ├── management/commands/cargar_productos.py
    └── templates/inventario/
        ├── base.html
        ├── dashboard.html
        ├── producto_list/form/delete/ajuste_stock.html
        ├── categoria_list/form/delete.html
        ├── venta_list/form/detail/delete.html
        └── login.html
```
