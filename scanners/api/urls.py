from django.urls import path
from .views import busqueda_dork
from .views import escaneo_dns

urlpatterns = [
    path('dorks/', busqueda_dork),
    path('scan/', escaneo_dns),
]