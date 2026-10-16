from django.db import models


class Comuna(models.Model):
    id_comu = models.AutoField(primary_key=True)
    nombre_comuna = models.CharField(max_length=50)
    zona_geografica = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comuna'


class CondicionUso(models.Model):
    id_cond = models.AutoField(primary_key=True)
    nombre_condicion = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'condicion_uso'


class EstadoPublicacion(models.Model):
    id_est_pub = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estado_publicacion'


class EstadoSolicitud(models.Model):
    id_est_sol = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estado_solicitud'


class Publicacion(models.Model):
    id_pub = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50)
    id_est_pub = models.ForeignKey(EstadoPublicacion, models.DO_NOTHING, db_column='id_est_pub')
    id_cond = models.ForeignKey(CondicionUso, models.DO_NOTHING, db_column='id_cond')
    id_usu = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usu')
    id_comu = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='id_comu')
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)

    class Meta:
        managed = False  # Le dice a Django que la tabla ya existe en MySQL
        db_table = 'publicacion'  

class RegistroImpactoAmbiental(models.Model):
    id_reg = models.AutoField(primary_key=True)
    id_sol = models.ForeignKey('SolicitudIntercambio', models.DO_NOTHING, db_column='id_sol')
    id_usu = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usu')
    id_comu = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='id_comu')
    categoria_objeto = models.CharField(max_length=50)
    kilos_basura_evitada = models.DecimalField(max_digits=6, decimal_places=2)
    co2_estimado_evitado = models.DecimalField(max_digits=6, decimal_places=2)
    fecha_impacto = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'registro_impacto_ambiental'


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(unique=True, max_length=30)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'


class SolicitudIntercambio(models.Model):
    id_sol = models.AutoField(primary_key=True)
    tipo_transaccion = models.CharField(max_length=20)
    id_est_sol = models.ForeignKey(EstadoSolicitud, models.DO_NOTHING, db_column='id_est_sol')
    punto_encuentro = models.CharField(max_length=150, blank=True, null=True)
    mensaje_inicial = models.TextField(blank=True, null=True)
    id_pub = models.ForeignKey(Publicacion, models.DO_NOTHING, db_column='id_pub')
    id_usu_interesado = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usu_interesado')
    fecha_solicitud = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'solicitud_intercambio'


class Usuario(models.Model):
    id_usu = models.AutoField(primary_key=True)
    nombre_usuario = models.CharField(unique=True, max_length=50)
    correo_electronico = models.CharField(unique=True, max_length=100)
    contrasena = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    id_comu = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='id_comu')
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol')
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'usuario'

class Conversacion(models.Model):
    id_conversacion = models.AutoField(primary_key=True, db_column='id_conversacion')
    usuario_cliente = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usu_cliente', related_name='chats_como_cliente')
    usuario_vendedor = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usu_vendedor', related_name='chats_como_vendedor')
    estado = models.CharField(max_length=50, db_column='estado', default='Activa')

    class Meta:
        managed = False
        db_table = 'conversacion'

class Mensaje(models.Model):
    id_mensaje = models.AutoField(primary_key=True, db_column='id_mensaje')
    id_conversacion = models.ForeignKey('Conversacion', models.DO_NOTHING, db_column='id_conversacion')
    id_usu = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usu')
    contenido = models.TextField(db_column='contenido')
    fecha_envio = models.DateTimeField(db_column='fecha_envio', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'mensaje'