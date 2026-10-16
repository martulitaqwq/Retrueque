"""
URL configuration for Trades project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin 

# solo paginas
from django.urls import path
from django.views.generic import TemplateView
from firstApp import views
from django.conf import settings
from django.conf.urls.static import static

# Importamos las vistas que creaste en tu views.py|
from firstApp.views import (
    PublicacionCreateView, PublicacionDetailView, PublicacionUpdateView, PublicacionDeleteView,
    CrearSolicitudView, CancelarSolicitudView, 
    AceptarYCrearChatView, RechazarSolicitudView,InicioListView, MisSolicitudesListView,
)

urlpatterns = [
    # 1. RUTAS  
    path('', InicioListView.as_view(), name='inicio'),
    path('publicaciones/', TemplateView.as_view(template_name='publicaciones/CreaPublic.html'), name='CreaPublic'),
    path('solicitudes/', MisSolicitudesListView.as_view(), name='me_solicitudes'),
    path('impacto/', views.impacto_ambiental, name='impacto_ambiental'),

    # 2. CRUD 
    # --- Rutas de Publicaciones ---
    path('publicar/', PublicacionCreateView.as_view(), name='publicacion_create'),
    path('publicacion/editar/<int:pk>/', PublicacionUpdateView.as_view(), name='publicacion_update'),
    path('publicacion/eliminar/<int:pk>/', PublicacionDeleteView.as_view(), name='publicacion_delete'),
    path('publicacion/<int:pk>/', PublicacionDetailView.as_view(), name='detalle_publicacion'),

    # --- Rutas de Solicitudes ---
    path('solicitud/crear/<int:pk>/', CrearSolicitudView.as_view(), name='crear_solicitud'),
    path('solicitud/cancelar/<int:pk>/', CancelarSolicitudView.as_view(), name='cancelar_solicitud'),
    path('solicitud/aceptar/<int:pk>/', AceptarYCrearChatView.as_view(), name='aceptar_solicitud'),
    path('solicitud/rechazar/<int:pk>/', RechazarSolicitudView.as_view(), name='rechazar_solicitud'),

    # --- Rutas del Chat ---
    path('chat/<int:id_conversacion>/', views.ver_chat, name='ver_chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)