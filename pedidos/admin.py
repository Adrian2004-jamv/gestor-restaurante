from django.contrib import admin

from .models import Cliente, Cocinero, Comanda, DetalleComanda, Entrega, EventoCatering, EventoCocinero, EventoUtileria, Insumo, Menu, MenuPlato, Plato, RecetaDetalle, Utileria

admin.site.register(Cliente)
admin.site.register(Cocinero)
admin.site.register(Comanda)
admin.site.register(DetalleComanda)
admin.site.register(Entrega)
admin.site.register(EventoCatering)
admin.site.register(EventoCocinero)
admin.site.register(EventoUtileria)
admin.site.register(Insumo)
admin.site.register(Menu)
admin.site.register(MenuPlato)
admin.site.register(Plato)
admin.site.register(RecetaDetalle)
admin.site.register(Utileria)
