from django.core.management.base import BaseCommand
from inventario.models import Producto, Categoria


PRODUCTOS_INICIALES = [
    ('CHETOS NARANJA',              4,  25.00, 'BOTANAS'),
    ('HOT NUTS MORADO',             5,  25.00, 'BOTANAS'),
    ('RULFES',                      4,  25.00, 'BOTANAS'),
    ('HOT NUTS NARANJA',            4,  25.00, 'BOTANAS'),
    ('FRITOS CHILE Y LIMON',        2,  25.00, 'BOTANAS'),
    ('ADOBADAS',                    5,  25.00, 'BOTANAS'),
    ('DORITOS NACHO',               5,  25.00, 'BOTANAS'),
    ('PALOMITAS MINI',              1,  15.00, 'BOTANAS'),
    ('SABRITAS NATURALES AMARILLA', 3,  25.00, 'BOTANAS'),
    ('SABRITAS FLAMIN HOTS',        4,  25.00, 'BOTANAS'),
    ('DORITOS INCOGNITO',           4,  25.00, 'BOTANAS'),
    ('CHETOS BOLITA',               4,  25.00, 'BOTANAS'),
    ('FRITOS CON CHORIZO',          2,  25.00, 'BOTANAS'),
    ('CHICHARRONES',                3,  25.00, 'BOTANAS'),
    ('FRITOS LIMON Y SAL',          3,  25.00, 'BOTANAS'),
    ('DORITOS FLAMIN HOTS',         4,  25.00, 'BOTANAS'),
    ('DORITOS DIABLO',              2,  25.00, 'BOTANAS'),
    ('CHIPS JALAPEÑO',              5,  25.00, 'BOTANAS'),
    ('CHIPS FUEGO',                 5,  25.00, 'BOTANAS'),
    ('LUCAS PANZON',                2,  15.00, 'DULCES'),
    ('COCA DE 600',                12,  27.00, 'BEBIDAS'),
    ('BOING',                       3,  20.00, 'BEBIDAS'),
    ('PINGÜINO',                    5,  29.00, 'POSTRES'),
    ('DORADITAS',                   3,  30.00, 'POSTRES'),
    ('DONITAS',                     2,  30.00, 'POSTRES'),
    ('POLVORONES',                  5,  27.00, 'POSTRES'),
    ('PRINCIPE',                    4,  27.00, 'POSTRES'),
    ('TRIKI TRAKES',                5,  26.00, 'POSTRES'),
    ('SPONCH',                      3,  26.00, 'POSTRES'),
    ('GANSITOS',                    5,  23.00, 'POSTRES'),
]


class Command(BaseCommand):
    help = 'Carga los productos iniciales de la tiendita'

    def handle(self, *args, **options):
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