from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio),
    path("dashboard/", views.dashboard),
    # CLIENTES
    path("clientes/", views.listado_clientes),
    path("nuevoCliente/", views.nuevo_cliente),
    path("guardar_Cliente/", views.guardar_cliente),
    path("editarCliente/<int:id>/", views.editar_cliente),
    path("actualizarCliente/<int:id>/", views.actualizar_cliente),
    path("eliminarCliente/<int:id>/", views.eliminar_cliente),
    # MENUS
    path("menus/", views.listado_menus),
    path("nuevoMenu/", views.nuevo_menu),
    path("guardarMenu/", views.guardar_menu),
    path("editarMenu/<int:id>/", views.editar_menu),
    path("actualizarMenu/<int:id>/", views.actualizar_menu),
    path("eliminarMenu/<int:id>/", views.eliminar_menu),
    # PLATOS
    path("platos/", views.listado_platos),
    path("nuevoPlato/", views.nuevo_plato),
    path("guardarPlato/", views.guardar_plato),
    path("editarPlato/<int:id>/", views.editar_plato),
    path("actualizarPlato/<int:id>/", views.actualizar_plato),
    path("eliminarPlato/<int:id>/", views.eliminar_plato),
    # EVENTOS
    path("eventos/", views.listado_eventos),
    path("nuevoEvento/", views.nuevo_evento),
    path("guardarEvento/", views.guardar_evento),
    path("editarEvento/<int:id>/", views.editar_evento),
    path("actualizarEvento/<int:id>/", views.actualizar_evento),
    path("eliminarEvento/<int:id>/", views.eliminar_evento),
    # INSUMOS
    path("insumos/", views.listado_insumos),
    path("nuevoInsumo/", views.nuevo_insumo),
    path("guardarInsumo/", views.guardar_insumo),
    path("editarInsumo/<int:id>/", views.editar_insumo),
    path("actualizarInsumo/<int:id>/", views.actualizar_insumo),
    path("eliminarInsumo/<int:id>/", views.eliminar_insumo),
    #recetas
    path("costeoPlato/<int:id>/", views.costeo_plato),
    path("guardarIngredienteReceta/", views.guardar_ingrediente_receta),
    path("eliminarIngredienteReceta/<int:id>/", views.eliminar_ingrediente_receta),
    #ensamblar
    path("ensamblarMenu/<int:id>/", views.ensamblar_menu),
    path("agregarPlatoMenu/", views.agregar_plato_menu),
    path("ordenarPlatosMenu/", views.ordenar_platos_menu),
    path("eliminarPlatoMenu/<int:id>/", views.eliminar_plato_menu),
    # calendario
    path("calendarioEventos/", views.calendario_eventos),
    path("datosCalendario/", views.datos_calendario),
    # COCINEROS
    path("cocineros/", views.listado_cocineros),
    path("nuevoCocinero/", views.nuevo_cocinero),
    path("guardarCocinero/", views.guardar_cocinero),
    path("editarCocinero/<int:id>/", views.editar_cocinero),
    path("actualizarCocinero/<int:id>/", views.actualizar_cocinero),
    path("eliminarCocinero/<int:id>/", views.eliminar_cocinero),
    path("asignarCocineros/<int:id>/", views.asignar_cocineros),
    path("guardarCocinerosEvento/<int:id>/", views.guardar_cocineros_evento),
    # UTILERÍA
    path("utileria/", views.listado_utileria),
    path("nuevaUtileria/", views.nueva_utileria),
    path("guardarUtileria/", views.guardar_utileria),
    path("editarUtileria/<int:id>/", views.editar_utileria),
    path("actualizarUtileria/<int:id>/", views.actualizar_utileria),
    path("eliminarUtileria/<int:id>/", views.eliminar_utileria),
    path("asignarUtileria/<int:id>/", views.asignar_utileria),
    path("guardarUtileriaEvento/<int:id>/", views.guardar_utileria_evento),
    path("eliminarUtileriaEvento/<int:id>/", views.eliminar_utileria_evento),
    # ENTREGAS
    path("entregas/", views.listado_entregas),
    path("nuevaEntrega/", views.nueva_entrega),
    path("guardarEntrega/", views.guardar_entrega),
    path("editarEntrega/<int:id>/", views.editar_entrega),
    path("actualizarEntrega/<int:id>/", views.actualizar_entrega),
    path("eliminarEntrega/<int:id>/", views.eliminar_entrega),
    # COMANDAS
    path("comandas/", views.listado_comandas),
    path("nuevaComanda/", views.nueva_comanda),
    path("guardarComanda/", views.guardar_comanda),
    path("actualizarEstadoComanda/<int:id>/", views.actualizar_estado_comanda),
    path("eliminarComanda/<int:id>/", views.eliminar_comanda),
    # REPORTES
    path("reporteMargenes/", views.reporte_margenes),
    path("reporteInsumosSemanal/", views.reporte_insumos_semanal),
    # DETALLE DEL MENÚ
    path("actualizarCantidadMenuPlato/<int:id>/", views.actualizar_cantidad_menu_plato),

]
