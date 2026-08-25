from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dsei-acceso/', auth_views.LoginView.as_view(template_name='inventario/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/catalogo/'), name='logout'),
    path('', include('inventario.urls')),
]

# Sirve los archivos subidos (fotos de productos) cuando DEBUG=True, es decir,
# cuando corres el proyecto en tu PC. En producción (Railway, DEBUG=False) esta
# línea no hace nada — ahí se necesita una configuración aparte para servir
# /media/ (lo vemos en el siguiente paso, junto con el volumen persistente).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)