"""
Comando para cargar los productos iniciales del Excel de la tiendita.
Uso: python manage.py cargar_productos
"""
from django.core.management.base import BaseCommand
from inventario.models import Producto, Categoria


PRODUCTOS_INICIALES = [
    # (nombre, stock_inicial, precio, categoria)
    ('CHETOS NARANJA',              4,  25.00, 'Botanas'),
    ('HOT NUTS MORADO',             5,  25.00, 'Botanas'),
    ('RULFES',                      4,  25.00, 'Botanas'),
    ('HOT NUTS NARANJA',            4,  25.00, 'Botanas'),
    ('FRITOS CHILE Y LIMON',        2,  25.00, 'Botanas'),
    ('ADOBADAS',                    5,  25.00, 'Botanas'),
    ('DORITOS NACHO',               5,  25.00, 'Botanas'),
    ('PALOMITAS MINI',              1,  15.00, 'Botanas'),
    ('SABRITAS NATURALES AMARILLA', 3,  25.00, 'Botanas'),
    ('SABRITAS FLAMIN HOTS',        4,  25.00, 'Botanas'),
    ('DORITOS INCOGNITO',           4,  25.00, 'Botanas'),
    ('CHETOS BOLITA',               4,  25.00, 'Botanas'),
    ('FRITOS CON CHORIZO',          2,  25.00, 'Botanas'),
    ('CHICHARRONES',                3,  25.00, 'Botanas'),
    ('FRITOS LIMON Y SAL',          3,  25.00, 'Botanas'),
    ('DORITOS FLAMIN HOTS',         4,  25.00, 'Botanas'),
    ('DORITOS DIABLO',              2,  25.00, 'Botanas'),
    ('CHIPS JALAPEÑO',              5,  25.00, 'Botanas'),
    ('CHIPS FUEGO',                 5,  25.00, 'Botanas'),
    ('LUCAS PANZON',                2,  15.00, 'Dulces'),
    ('COCA DE 600',                12,  27.00, 'Bebidas'),
    ('BOING',                       3,  20.00, 'Bebidas'),
    ('PINGÜINO',                    5,  29.00, 'Postres'),
    ('DORADITAS',                   3,  30.00, 'Postres'),
    ('DONITAS',                     2,  30.00, 'Postres'),
    ('POLVORONES',                  5,  27.00, 'Postres'),
    ('PRINCIPE',                    4,  27.00, 'Postres'),
    ('TRIKI TRAKES',                5,  26.00, 'Postres'),
    ('SPONCH',                      3,  26.00, 'Postres'),
    ('GANSITOS',                    5,  23.00, 'Postres'),
]


class Command(BaseCommand):
    help = 'Carga los productos iniciales de la tiendita desde el Excel original'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los productos antes de cargar (¡cuidado!)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            Producto.objects.all().delete()
            self.stdout.write(self.style.WARNING('Productos eliminados.'))

        creados = 0
        existentes = 0

        for nombre, stock, precio, cat_nombre in PRODUCTOS_INICIALES:
            categoria, _ = Categoria.objects.get_or_create(nombre=cat_nombre)

            producto, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'categoria': categoria,
                    'stock_inicial': stock,
                    'stock_actual': stock,
                    'precio': precio,
                    'activo': True,
                }
            )

            if created:
                creados += 1
                self.stdout.write(f'  ✅ {nombre} — ${precio} — stock: {stock}')
            else:
                existentes += 1
                self.stdout.write(self.style.WARNING(f'  ⚠️  {nombre} ya existe, omitido.'))

        self.stdout.write(self.style.SUCCESS(
            f'\n✔ Listo. {creados} productos creados, {existentes} ya existían.'
        ))
