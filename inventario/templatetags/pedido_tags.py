from django import template
from inventario.models import Pedido

register = template.Library()

@register.simple_tag
def pedidos_nuevos():
    return Pedido.objects.filter(estado='nuevo').count()