from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.db import models # <-- Necesario para el buscador con Q
from django.views.generic import DetailView
from django import forms
from django.db import IntegrityError
from django.shortcuts import redirect
from .models import Conversacion, Mensaje
# --- MODELOS ---
from .models import (
    Publicacion, SolicitudIntercambio, EstadoSolicitud, 
    Usuario, RegistroImpactoAmbiental, EstadoPublicacion, 
    CondicionUso, Comuna
)

# --- FORMULARIOS ---
from .forms import PublicacionForm
# Publicacion
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Publicacion
from .forms import PublicacionForm 

# tabla Solicitud 
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import SolicitudIntercambio, Usuario

#impactoAmbiental 
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import RegistroImpactoAmbiental, Usuario

# ==========================================
# VISTA DE INICIO (Listado y Buscador por Palabras Clave)
# ==========================================
class InicioListView(ListView):
    model = Publicacion
    template_name = 'base.html'
    context_object_name = 'publicaciones'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-fecha_publicacion')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(titulo__icontains=query) | 
                models.Q(descripcion__icontains=query) |
                models.Q(categoria__icontains=query)
            )
        return queryset

# ==========================================
# CRUD DE PUBLICACIONES
# ==========================================
class PublicacionCreateView(SuccessMessageMixin, CreateView):
    model = Publicacion
    form_class = PublicacionForm
    template_name = 'publicaciones/CreaPublic.html'
    success_url = reverse_lazy('inicio')
    success_message = "¡Trade publicado con éxito!"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.id_est_pub = EstadoPublicacion.objects.first() 
        self.object.id_usu = Usuario.objects.first()             
        self.object.id_comu = Comuna.objects.first()             
        
        estado_html = self.request.POST.get('estado', 'nuevo')
        condiciones_map = {
            'nuevo': 'Nuevo',
            'como_nuevo': 'Como nuevo',
            'poco_usado': 'Poco usado',
            'usado': 'Usado',
            'muy_usado': 'Muy usado',
            'roto': 'Roto / para repuestos'
        }
        nombre_condicion = condiciones_map.get(estado_html, 'Nuevo')
        
        self.object.id_cond = (
            CondicionUso.objects.filter(nombre_condicion__icontains=nombre_condicion).first() 
            or CondicionUso.objects.first()
        )
        
        self.object.save()
        return redirect(self.success_url)
    
class PublicacionUpdateView(SuccessMessageMixin, UpdateView):
    model = Publicacion
    template_name = 'publicaciones/editar_publicacion.html'
    fields = ['descripcion', 'categoria']
    context_object_name = 'publicacion'
    success_message = "¡Publicación actualizada con éxito!"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        opciones_categorias = [
            ('Tecnología', 'Tecnología'),
            ('Ropa', 'Ropa'),
            ('Libros', 'Libros'),
            ('Accesorios', 'Accesorios'),
            ('Muebles', 'Muebles'),
            ('Deportes', 'Deportes'),
            ('Hogar', 'Hogar'),
            ('Juguetes', 'Juguetes'),
            ('Autos', 'Autos'),
            ('Motos', 'Motos'),
            ('Bicicletas', 'Bicicletas'),
            ('Repuestos', 'Repuestos'),
            ('Otros', 'Otros'),
        ]
        form.fields['categoria'].widget = forms.Select(
            choices=opciones_categorias,
            attrs={'class': 'form-select'}
        )
        form.fields['descripcion'].widget = forms.Textarea(
            attrs={'class': 'form-control', 'rows': 4}
        )
        return form

    def get_success_url(self):
        return reverse_lazy('detalle_publicacion', kwargs={'pk': self.object.pk})
    
class PublicacionDeleteView(DeleteView):
    model = Publicacion
    success_url = reverse_lazy('inicio')

    def post(self, request, *args, **kwargs):
        try:
            respuesta = super().post(request, *args, **kwargs)
            messages.success(request, "¡El trade ha sido eliminado!")
            return respuesta
        except IntegrityError:
            messages.warning(
                request,
                "No se puede eliminar este trade porque ya tiene una solicitud de intercambio asociada."
            )
            return redirect('inicio')
class PublicacionDetailView(DetailView):
    model = Publicacion
    template_name = 'publicaciones/detalle_publicacion.html'
    context_object_name = 'publicacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Sin login: revisa directamente si esta publicación ya tiene una solicitud enviada
        context['ya_solicitado'] = SolicitudIntercambio.objects.filter(id_pub=self.object).exists()
        return context
# ==========================================
# CRUD DE SOLICITUDES (EMISOR Y RECEPTOR)
# ==========================================
class MisSolicitudesListView(ListView):
    model = SolicitudIntercambio
    template_name = 'solicitudes/mis_solicitudes.html'
    context_object_name = 'solicitudes_enviadas'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            usuario_actual = Usuario.objects.filter(correo_electronico=self.request.user.email).first()
        else:
            usuario_actual = Usuario.objects.first()

        if usuario_actual:
            return SolicitudIntercambio.objects.filter(id_usu_interesado=usuario_actual)
        return SolicitudIntercambio.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            usuario_actual = Usuario.objects.filter(correo_electronico=self.request.user.email).first()
        else:
            usuario_actual = Usuario.objects.first()

        if usuario_actual:
            context['solicitudes_recibidas'] = SolicitudIntercambio.objects.filter(id_pub__id_usu=usuario_actual)
        else:
            context['solicitudes_recibidas'] = []
            
        return context

class CrearSolicitudView(View):
    def post(self, request, pk):
        publicacion = get_object_or_404(Publicacion, pk=pk)
        
        # Verificamos si hay un usuario logueado, si no, usamos el primero de la base de datos para pruebas
        if request.user.is_authenticated:
            usuario_actual = Usuario.objects.filter(correo_electronico=request.user.email).first()
        else:
            usuario_actual = None
            
        # Si no se encuentra vinculado por correo, tomamos el primer usuario disponible para evitar el error
        if not usuario_actual:
            usuario_actual = Usuario.objects.first()

        # Búsqueda segura del estado para evitar errores 404
        estado_pendiente = (
            EstadoSolicitud.objects.filter(nombre_estado__icontains='Pendiente').first() or 
            EstadoSolicitud.objects.first()
        )
        
        if not estado_pendiente:
            messages.error(request, "Error: No hay estados de solicitud configurados.")
            return redirect('detalle_publicacion', pk=pk)
        
        SolicitudIntercambio.objects.create(
            id_pub=publicacion,
            id_usu_interesado=usuario_actual,
            id_est_sol=estado_pendiente
        )
        
        messages.success(request, "¡Solicitud enviada al vendedor!")
        return redirect('detalle_publicacion', pk=pk) 

        

class CancelarSolicitudView(View):
    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudIntercambio, pk=pk)
        solicitud.delete()
        messages.success(request, "Has cancelado tu solicitud de trade.")
        return redirect('me_solicitudes')

class AceptarYCrearChatView(View):
    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudIntercambio, pk=pk)
        estado_aceptado = (
            EstadoSolicitud.objects.filter(nombre_estado__icontains='Aceptado').first() or 
            EstadoSolicitud.objects.first()
        )
        if estado_aceptado:
            solicitud.id_est_sol = estado_aceptado
            solicitud.save()
        
        messages.success(request, "¡Trade aceptado! Se ha generado el chat.")
        return redirect('me_solicitudes')

class RechazarSolicitudView(View):
    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudIntercambio, pk=pk)
        solicitud.delete()
        messages.error(request, "Solicitud rechazada y eliminada.")
        return redirect('me_solicitudes')

# ==========================================
# CRUD DE CHAT
# ==========================================
from .models import Conversacion, Mensaje

from django.shortcuts import render, redirect, get_object_or_404
from .models import Conversacion, Mensaje, Usuario

def ver_chat(request, id_conversacion):
    conversacion = get_object_or_404(Conversacion, pk=id_conversacion)
    mensajes = Mensaje.objects.filter(id_conversacion=conversacion).order_by('fecha_envio')
    
    # Usuario por defecto para la sesión local
    usuario_actual = get_object_or_404(Usuario, pk=1)

    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            Mensaje.objects.create(
                id_conversacion=conversacion,
                id_usu=usuario_actual,
                contenido=contenido
            )
            return redirect('ver_chat', id_conversacion=conversacion.id_conversacion)

    context = {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'usuario_actual': usuario_actual
    }
    return render(request, 'chat.html', context)

from .models import Conversacion, SolicitudIntercambio

class AceptarYCrearChatView(View):
    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudIntercambio, pk=pk)
        
        # Cambiar el estado de la solicitud a Aceptado (ID 2 o el que corresponda)
        estado_aceptado = get_object_or_404(EstadoSolicitud, nombre_estado__iexact='Aceptado')
        solicitud.id_est_sol = estado_aceptado
        solicitud.save()

        # Crear o buscar la conversación asociada a esta solicitud/trade
        conversacion, created = Conversacion.objects.get_or_create(
            usuario_cliente=solicitud.id_usu_interesado,
            usuario_vendedor=solicitud.id_pub.id_usu,
            defaults={'estado': 'Activa'}
        )

        messages.success(request, "¡Trade aceptado! Se ha generado el chat.")
        return redirect('me_solicitudes')

class AceptarYCrearChatView(View):
    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudIntercambio, pk=pk)
        
        solicitud.id_est_sol_id = 2
        solicitud.save()

        # Crear o buscar la conversación asociada a este trueque
        conversacion, created = Conversacion.objects.get_or_create(
            usuario_cliente=solicitud.id_usu_interesado,
            usuario_vendedor=solicitud.id_pub.id_usu,
            defaults={'estado': 'Activa'}
        )

        messages.success(request, "¡Trade aceptado! Se ha generado el chat.")
        return redirect('me_solicitudes')

def impacto_ambiental(request):
    # Contamos cuántas solicitudes de trueque están aceptadas en la base de datos (por ejemplo, id_est_sol == 2 o según tu BD)
    # Si prefieres contar todas las solicitudes registradas, puedes usar SolicitudIntercambio.objects.count()
    trueques_exitosos = SolicitudIntercambio.objects.filter(id_est_sol=2).count()
    
    # Transformamos los trueques en métricas ecológicas (ODS 12)
    kg_co2_evitado = trueques_exitosos * 5.0
    kg_residuos_evitados = trueques_exitosos * 2.0
    agua_ahorrada_litros = trueques_exitosos * 45.0

    context = {
        'trueques_exitosos': trueques_exitosos,
        'kg_co2_evitado': kg_co2_evitado,
        'kg_residuos_evitados': kg_residuos_evitados,
        'agua_ahorrada_litros': agua_ahorrada_litros,
    }
    
    return render(request, 'impacto/impacto_ambiental.html', context)

# Compatibilidad con MariaDB / XAMPP
from django.db.backends.mysql.features import DatabaseFeatures

DatabaseFeatures.can_return_columns_from_insert = False
DatabaseFeatures.can_return_rows_from_bulk_insert = False