from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from .models import Cliente, EventoCatering, Insumo, Menu, Plato, RecetaDetalle


class GestorRestauranteTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(tipo="PERSONA", nombre="Cliente prueba", identificacion="9999999999", telefono="0999999999")
        self.menu = Menu.objects.create(nombre="Menú prueba", precio_por_persona=Decimal("10.00"))
        self.plato = Plato.objects.create(nombre="Plato prueba", tiempo_menu="PRINCIPAL", precio_venta=Decimal("8.00"), tiempo_preparacion=20)
        self.insumo = Insumo.objects.create(nombre="Insumo prueba", unidad_medida="KG", costo_unitario=Decimal("2.00"), stock_actual=Decimal("10.00"), stock_minimo=Decimal("2.00"))
        RecetaDetalle.objects.create(plato=self.plato, insumo=self.insumo, cantidad=Decimal("0.500"))
        self.evento = EventoCatering.objects.create(cliente=self.cliente, menu=self.menu, nombre_evento="Evento prueba", tipo_servicio="SOCIAL", fecha_inicio=timezone.now() + timedelta(days=1), fecha_fin=timezone.now() + timedelta(days=1, hours=3), direccion="Dirección", numero_personas=20, estado="CONFIRMADO", total_contratado=Decimal("200.00"), anticipo=Decimal("50.00"))

    def test_costo_y_margen_del_plato(self):
        self.assertEqual(self.plato.costo_receta(), Decimal("1.00"))
        self.assertEqual(self.plato.margen_contribucion(), Decimal("7.00"))

    def test_dashboard_responde(self):
        respuesta = self.client.get("/dashboard/")
        self.assertEqual(respuesta.status_code, 200)

    def test_calendario_json_responde(self):
        respuesta = self.client.get("/datosCalendario/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Evento prueba")

    def test_paginas_nuevas_responden(self):
        rutas = ["/cocineros/", "/utileria/", "/entregas/", "/comandas/", "/reporteMargenes/", "/reporteInsumosSemanal/"]
        for ruta in rutas:
            self.assertEqual(self.client.get(ruta).status_code, 200)
