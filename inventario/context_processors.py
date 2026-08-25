# inventario/context_processors.py
from .models import Pedido

def pedidos_nuevos(request):
    if not request.user.is_authenticated:
        return {'total_nuevos': 0}
    total = Pedido.objects.filter(estado='nuevo').count()
    return {'total_nuevos': total}