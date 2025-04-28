from django.urls import path
from .views import busqueda_dork

urlpatterns = [
    path('dorks/', busqueda_dork),
]