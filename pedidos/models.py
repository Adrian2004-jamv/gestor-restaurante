from django.db import models

# Create your models here.
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

class Cliente(models.Model):
    TIPO_CLIENTE = [
        ("PERSONA", "Persona natural"),
        ("EMPRESA", "Empresa"),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CLIENTE,
        default="PERSONA"
    )
    nombre = models.CharField(max_length=150)
    identificacion = models.CharField(
        max_length=20,
        unique=True,
        help_text="Cédula o RUC"
    )
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Insumo(models.Model):
    UNIDADES = [
        ("KG", "Kilogramos"),
        ("G", "Gramos"),
        ("L", "Litros"),
        ("ML", "Mililitros"),
        ("UND", "Unidades"),
    ]

    nombre = models.CharField(max_length=120, unique=True)
    unidad_medida = models.CharField(max_length=5, choices=UNIDADES)
    costo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    stock_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_medida_display()})"

class Plato(models.Model):
    TIEMPOS_MENU = [
        ("ENTRADA", "Entrada"),
        ("PRINCIPAL", "Plato principal"),
        ("ACOMPANAMIENTO", "Acompañamiento"),
        ("POSTRE", "Postre"),
        ("BEBIDA", "Bebida"),
        ("OTRO", "Otro"),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    tiempo_menu = models.CharField(
        max_length=20,
        choices=TIEMPOS_MENU
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    tiempo_preparacion = models.PositiveIntegerField(
        default=15,
        help_text="Tiempo aproximado en minutos"
    )
    imagen = models.ImageField(
        upload_to="platos/",
        blank=True,
        null=True
    )
    tecla_rapida = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text="Número utilizado por Hotkeys-js"
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["tiempo_menu", "nombre"]

    def __str__(self):
        return self.nombre

    def costo_receta(self):
        expresion = ExpressionWrapper(
            F("cantidad") * F("insumo__costo_unitario"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2
            )
        )

        resultado = self.ingredientes_receta.aggregate(
            total=Sum(expresion)
        )

        return resultado["total"] or Decimal("0.00")

    def margen_contribucion(self):
        return self.precio_venta - self.costo_receta()

    def porcentaje_margen(self):
        if self.precio_venta == 0:
            return Decimal("0.00")

        return (
            self.margen_contribucion() / self.precio_venta
        ) * 100

class RecetaDetalle(models.Model):
    plato = models.ForeignKey(
        Plato,
        on_delete=models.CASCADE,
        related_name="ingredientes_receta"
    )

    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.PROTECT,
        related_name="recetas"
    )

    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="Cantidad necesaria para una porción"
    )

    def subtotal(self):
        return self.cantidad * self.insumo.costo_unitario

    def __str__(self):
        return f"{self.plato.nombre} - {self.insumo.nombre}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["plato", "insumo"],
                name="ingrediente_unico_por_plato"
            )
        ]

    def __str__(self):
        return f"{self.plato} - {self.insumo}"

class Menu(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio_por_persona = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    platos = models.ManyToManyField(
        Plato,
        through="MenuPlato",
        related_name="menus"
    )

    def __str__(self):
        return self.nombre


class MenuPlato(models.Model):
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="detalles_menu"
    )
    plato = models.ForeignKey(
        Plato,
        on_delete=models.PROTECT,
        related_name="detalles_menu"
    )
    tiempo_menu = models.CharField(
        max_length=20,
        choices=Plato.TIEMPOS_MENU
    )
    orden = models.PositiveIntegerField(default=1)
    cantidad_por_persona = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=1
    )

    class Meta:
        ordering = ["tiempo_menu", "orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["menu", "plato"],
                name="plato_unico_por_menu"
            )
        ]

    def __str__(self):
        return f"{self.menu} - {self.plato}"

class Cocinero(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="perfil_cocinero"
    )
    nombres = models.CharField(max_length=150)
    identificacion = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    especialidad = models.CharField(max_length=120, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombres

class EventoCatering(models.Model):
    ESTADOS = [
        ("COTIZADO", "Cotizado"),
        ("CONFIRMADO", "Confirmado"),
        ("PREPARACION", "En preparación"),
        ("EN_CURSO", "En curso"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    ]

    TIPOS_SERVICIO = [
        ("BODA", "Boda"),
        ("CUMPLEANOS", "Cumpleaños"),
        ("EMPRESARIAL", "Evento empresarial"),
        ("GRADUACION", "Graduación"),
        ("SOCIAL", "Evento social"),
        ("OTRO", "Otro"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="eventos"
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.PROTECT,
        related_name="eventos"
    )
    nombre_evento = models.CharField(max_length=180)
    tipo_servicio = models.CharField(
        max_length=20,
        choices=TIPOS_SERVICIO,
        default="OTRO"
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    direccion = models.CharField(max_length=255)
    numero_personas = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="COTIZADO"
    )
    total_contratado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    anticipo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    cocineros = models.ManyToManyField(
        Cocinero,
        through="EventoCocinero",
        related_name="eventos"
    )

    class Meta:
        ordering = ["fecha_inicio"]

    def __str__(self):
        return self.nombre_evento

    def saldo_pendiente(self):
        return self.total_contratado - self.anticipo


class EventoCocinero(models.Model):
    ROLES = [
        ("JEFE", "Chef principal"),
        ("COCINERO", "Cocinero"),
        ("AYUDANTE", "Ayudante de cocina"),
        ("PASTELERO", "Pastelero"),
    ]

    evento = models.ForeignKey(
        EventoCatering,
        on_delete=models.CASCADE,
        related_name="asignaciones_cocineros"
    )
    cocinero = models.ForeignKey(
        Cocinero,
        on_delete=models.PROTECT,
        related_name="asignaciones"
    )
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default="COCINERO"
    )
    horas_asignadas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["evento", "cocinero"],
                name="cocinero_unico_por_evento"
            )
        ]

    def __str__(self):
        return f"{self.evento} - {self.cocinero}"

class Utileria(models.Model):
    CATEGORIAS = [
        ("MESA", "Mesas"),
        ("SILLA", "Sillas"),
        ("VAJILLA", "Vajilla"),
        ("CUBIERTOS", "Cubiertos"),
        ("MANTELERIA", "Mantelería"),
        ("DECORACION", "Decoración"),
        ("EQUIPO", "Equipo de cocina"),
        ("OTRO", "Otro"),
    ]

    nombre = models.CharField(max_length=150)
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS
    )
    cantidad_total = models.PositiveIntegerField(default=0)
    costo_reposicion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class EventoUtileria(models.Model):
    ESTADOS = [
        ("RESERVADA", "Reservada"),
        ("DESPACHADA", "Despachada"),
        ("DEVUELTA", "Devuelta"),
        ("DANADA", "Dañada"),
        ("PERDIDA", "Perdida"),
    ]

    evento = models.ForeignKey(
        EventoCatering,
        on_delete=models.CASCADE,
        related_name="utileria_asignada"
    )
    utileria = models.ForeignKey(
        Utileria,
        on_delete=models.PROTECT,
        related_name="reservas"
    )
    cantidad = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="RESERVADA"
    )
    cantidad_devuelta = models.PositiveIntegerField(default=0)
    observaciones = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["evento", "utileria"],
                name="utileria_unica_por_evento"
            )
        ]

    def __str__(self):
        return f"{self.evento} - {self.utileria}"

class Comanda(models.Model):
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("PREPARANDO", "Preparando"),
        ("LISTA", "Lista"),
        ("DESPACHADA", "Despachada"),
        ("CANCELADA", "Cancelada"),
    ]

    codigo = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    evento = models.ForeignKey(
        EventoCatering,
        on_delete=models.CASCADE,
        related_name="comandas"
    )
    numero_mesa = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="PENDIENTE"
    )
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_despacho = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f"CMD-{uuid.uuid4().hex[:8].upper()}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo

class DetalleComanda(models.Model):
    comanda = models.ForeignKey(
        Comanda,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    plato = models.ForeignKey(
        Plato,
        on_delete=models.PROTECT,
        related_name="detalles_comanda"
    )
    cantidad = models.PositiveIntegerField(default=1)
    observaciones = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.comanda} - {self.plato}"

class Entrega(models.Model):
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("PREPARANDO", "Preparando carga"),
        ("EN_RUTA", "En ruta"),
        ("ENTREGADA", "Entregada"),
        ("INCIDENCIA", "Con incidencia"),
        ("CANCELADA", "Cancelada"),
    ]

    evento = models.ForeignKey(
        EventoCatering,
        on_delete=models.CASCADE,
        related_name="entregas"
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entregas_asignadas"
    )
    fecha_salida = models.DateTimeField()
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    direccion_entrega = models.CharField(max_length=255)
    vehiculo = models.CharField(max_length=100, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="PENDIENTE"
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["fecha_salida"]

    def __str__(self):
        return f"Entrega de {self.evento}"