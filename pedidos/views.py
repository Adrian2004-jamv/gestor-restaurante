from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Cliente, Cocinero, Comanda, DetalleComanda, Entrega, EventoCatering, EventoCocinero, EventoUtileria, Insumo, Menu, MenuPlato, Plato, RecetaDetalle, Utileria

# INICIO Y DASHBOARD

def inicio(request):
    platos = Plato.objects.filter(activo=True)[:6]

    return render(
        request,
        "inicio.html",
        {"platos": platos}
    )

def dashboard(request):
    totales_eventos = EventoCatering.objects.exclude(estado="CANCELADO").aggregate(
        total=Sum("total_contratado"),
        anticipo=Sum("anticipo")
    )

    saldo_pendiente = (totales_eventos["total"] or Decimal("0.00")) - (totales_eventos["anticipo"] or Decimal("0.00"))

    platos_margen = []
    for plato in Plato.objects.filter(activo=True):
        costo = plato.costo_receta()
        margen = plato.precio_venta - costo
        porcentaje = (margen / plato.precio_venta) * 100 if plato.precio_venta else Decimal("0.00")
        platos_margen.append({
            "plato": plato,
            "costo": costo,
            "margen": margen,
            "porcentaje": porcentaje,
        })

    platos_margen.sort(key=lambda elemento: elemento["margen"], reverse=True)

    contexto = {
        "total_clientes": Cliente.objects.filter(activo=True).count(),
        "total_eventos": EventoCatering.objects.count(),
        "total_menus": Menu.objects.filter(activo=True).count(),
        "total_platos": Plato.objects.filter(activo=True).count(),
        "total_cocineros": Cocinero.objects.filter(activo=True).count(),
        "total_utileria": Utileria.objects.filter(activo=True).count(),
        "entregas_pendientes": Entrega.objects.exclude(estado__in=["ENTREGADA", "CANCELADA"]).count(),
        "comandas_pendientes": Comanda.objects.exclude(estado__in=["DESPACHADA", "CANCELADA"]).count(),
        "insumos_bajos": 0,
        "saldo_pendiente": saldo_pendiente,
        "proximos_eventos": EventoCatering.objects.select_related("cliente", "menu").filter(fecha_inicio__gte=timezone.now()).exclude(estado="CANCELADO").order_by("fecha_inicio")[:5],
        "stock_bajo": [insumo for insumo in Insumo.objects.filter(activo=True).order_by("nombre") if insumo.stock_actual <= insumo.stock_minimo][:5],
        "mejores_margenes": platos_margen[:5],
    }

    contexto["insumos_bajos"] = len([insumo for insumo in Insumo.objects.filter(activo=True) if insumo.stock_actual <= insumo.stock_minimo])

    return render(request, "dashboard.html", contexto)


# CLIENTES

def listado_clientes(request):
    clientes = Cliente.objects.filter(activo=True).order_by("nombre")

    return render(
        request,
        "clientes/listado.html",
        {"clientes": clientes}
    )

def nuevo_cliente(request):
    return render(request, "clientes/formulario.html")

def guardar_cliente(request):
    if request.method == "POST":
        Cliente.objects.create(
            tipo=request.POST["tipo"],
            nombre=request.POST["nombre"],
            identificacion=request.POST["identificacion"],
            telefono=request.POST["telefono"],
            correo=request.POST.get("correo", ""),
            direccion=request.POST.get("direccion", ""),
            activo=request.POST.get("activo") == "on",
        )

    return redirect("/clientes/")

def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    return render(
        request,
        "clientes/formulario.html",
        {"cliente": cliente}
    )

def actualizar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == "POST":
        cliente.tipo = request.POST["tipo"]
        cliente.nombre = request.POST["nombre"]
        cliente.identificacion = request.POST["identificacion"]
        cliente.telefono = request.POST["telefono"]
        cliente.correo = request.POST.get("correo", "")
        cliente.direccion = request.POST.get("direccion", "")
        cliente.activo = request.POST.get("activo") == "on"

        cliente.save()

    return redirect("/clientes/")

def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == "POST":
        cliente.activo = False
        cliente.save()

    return redirect("/clientes/")

# MENÚS

def listado_menus(request):
    menus = Menu.objects.filter(activo=True).order_by("nombre")

    return render(
        request,
        "menus/listado.html",
        {"menus": menus}
    )

def nuevo_menu(request):
    return render(request, "menus/formulario.html")

def guardar_menu(request):
    if request.method == "POST":
        Menu.objects.create(
            nombre=request.POST["nombre"],
            descripcion=request.POST.get("descripcion", ""),
            precio_por_persona=request.POST["precio_por_persona"],
            activo=request.POST.get("activo") == "on",
        )

    return redirect("/menus/")

def editar_menu(request, id):
    menu = get_object_or_404(Menu, id=id)

    return render(
        request,
        "menus/formulario.html",
        {"menu": menu}
    )

def actualizar_menu(request, id):
    menu = get_object_or_404(Menu, id=id)

    if request.method == "POST":
        menu.nombre = request.POST["nombre"]
        menu.descripcion = request.POST.get("descripcion", "")
        menu.precio_por_persona = request.POST["precio_por_persona"]
        menu.activo = request.POST.get("activo") == "on"

        menu.save()

    return redirect("/menus/")

def eliminar_menu(request, id):
    menu = get_object_or_404(Menu, id=id)

    if request.method == "POST":
        menu.activo = False
        menu.save()

    return redirect("/menus/")


# PLATOS

def listado_platos(request):
    platos = Plato.objects.filter(activo=True).order_by(
        "tiempo_menu",
        "nombre"
    )

    return render(
        request,
        "platos/listado.html",
        {"platos": platos}
    )

def nuevo_plato(request):
    return render(request, "platos/formulario.html")

def guardar_plato(request):
    if request.method == "POST":
        tecla_rapida = request.POST.get("tecla_rapida")

        if tecla_rapida == "":
            tecla_rapida = None

        Plato.objects.create(
            nombre=request.POST["nombre"],
            descripcion=request.POST.get("descripcion", ""),
            tiempo_menu=request.POST["tiempo_menu"],
            precio_venta=request.POST["precio_venta"],
            tiempo_preparacion=request.POST["tiempo_preparacion"],
            imagen=request.FILES.get("imagen"),
            tecla_rapida=tecla_rapida,
            activo=request.POST.get("activo") == "on",
        )

    return redirect("/platos/")

def editar_plato(request, id):
    plato = get_object_or_404(Plato, id=id)

    return render(
        request,
        "platos/formulario.html",
        {"plato": plato}
    )

def actualizar_plato(request, id):
    plato = get_object_or_404(Plato, id=id)

    if request.method == "POST":
        tecla_rapida = request.POST.get("tecla_rapida")

        if tecla_rapida == "":
            tecla_rapida = None

        plato.nombre = request.POST["nombre"]
        plato.descripcion = request.POST.get("descripcion", "")
        plato.tiempo_menu = request.POST["tiempo_menu"]
        plato.precio_venta = request.POST["precio_venta"]
        plato.tiempo_preparacion = request.POST["tiempo_preparacion"]
        plato.tecla_rapida = tecla_rapida
        plato.activo = request.POST.get("activo") == "on"

        if request.FILES.get("imagen"):
            plato.imagen = request.FILES["imagen"]

        plato.save()

    return redirect("/platos/")

def eliminar_plato(request, id):
    plato = get_object_or_404(Plato, id=id)

    if request.method == "POST":
        plato.activo = False
        plato.save()

    return redirect("/platos/")


# EVENTOS DE CATERING

def listado_eventos(request):
    eventos = EventoCatering.objects.select_related(
        "cliente",
        "menu"
    ).order_by("-fecha_inicio")

    return render(
        request,
        "eventos/listado.html",
        {"eventos": eventos}
    )

def nuevo_evento(request):
    clientes = Cliente.objects.filter(activo=True).order_by("nombre")
    menus = Menu.objects.filter(activo=True).order_by("nombre")

    return render(
        request,
        "eventos/formulario.html",
        {
            "clientes": clientes,
            "menus": menus,
        }
    )

def guardar_evento(request):
    if request.method == "POST":
        cliente = get_object_or_404(
            Cliente,
            id=request.POST["cliente_id"]
        )

        menu = get_object_or_404(
            Menu,
            id=request.POST["menu_id"]
        )

        EventoCatering.objects.create(
            cliente=cliente,
            menu=menu,
            nombre_evento=request.POST["nombre_evento"],
            tipo_servicio=request.POST["tipo_servicio"],
            fecha_inicio=request.POST["fecha_inicio"],
            fecha_fin=request.POST["fecha_fin"],
            direccion=request.POST["direccion"],
            numero_personas=request.POST["numero_personas"],
            estado=request.POST["estado"],
            total_contratado=request.POST["total_contratado"],
            anticipo=request.POST["anticipo"],
            observaciones=request.POST.get("observaciones", ""),
        )

    return redirect("/eventos/")

def editar_evento(request, id):
    evento = get_object_or_404(EventoCatering, id=id)

    clientes = Cliente.objects.filter(activo=True).order_by("nombre")
    menus = Menu.objects.filter(activo=True).order_by("nombre")

    return render(
        request,
        "eventos/formulario.html",
        {
            "evento": evento,
            "clientes": clientes,
            "menus": menus,
        }
    )

def actualizar_evento(request, id):
    evento = get_object_or_404(EventoCatering, id=id)

    if request.method == "POST":
        evento.cliente = get_object_or_404(
            Cliente,
            id=request.POST["cliente_id"]
        )

        evento.menu = get_object_or_404(
            Menu,
            id=request.POST["menu_id"]
        )

        evento.nombre_evento = request.POST["nombre_evento"]
        evento.tipo_servicio = request.POST["tipo_servicio"]
        evento.fecha_inicio = request.POST["fecha_inicio"]
        evento.fecha_fin = request.POST["fecha_fin"]
        evento.direccion = request.POST["direccion"]
        evento.numero_personas = request.POST["numero_personas"]
        evento.estado = request.POST["estado"]
        evento.total_contratado = request.POST["total_contratado"]
        evento.anticipo = request.POST["anticipo"]
        evento.observaciones = request.POST.get("observaciones", "")

        evento.save()

    return redirect("/eventos/")

def eliminar_evento(request, id):
    evento = get_object_or_404(EventoCatering, id=id)

    if request.method == "POST":
        evento.delete()

    return redirect("/eventos/")

# INSUMOS

def listado_insumos(request):
    insumos = Insumo.objects.filter(activo=True).order_by("nombre")
    return render(request, "insumos/listado.html", {"insumos": insumos})

def nuevo_insumo(request):
    return render(request, "insumos/formulario.html")

def guardar_insumo(request):
    if request.method == "POST":
        Insumo.objects.create(
            nombre=request.POST["nombre"],
            unidad_medida=request.POST["unidad_medida"],
            costo_unitario=request.POST["costo_unitario"],
            stock_actual=request.POST["stock_actual"],
            stock_minimo=request.POST["stock_minimo"],
            activo=request.POST.get("activo") == "on",
        )

    return redirect("/insumos/")

def editar_insumo(request, id):
    insumo = get_object_or_404(Insumo, id=id)
    return render(request, "insumos/formulario.html", {"insumo": insumo})

def actualizar_insumo(request, id):
    insumo = get_object_or_404(Insumo, id=id)

    if request.method == "POST":
        insumo.nombre = request.POST["nombre"]
        insumo.unidad_medida = request.POST["unidad_medida"]
        insumo.costo_unitario = request.POST["costo_unitario"]
        insumo.stock_actual = request.POST["stock_actual"]
        insumo.stock_minimo = request.POST["stock_minimo"]
        insumo.activo = request.POST.get("activo") == "on"
        insumo.save()

    return redirect("/insumos/")

def eliminar_insumo(request, id):
    insumo = get_object_or_404(Insumo, id=id)

    if request.method == "POST":
        insumo.activo = False
        insumo.save()

    return redirect("/insumos/")

# RECETAS
def costeo_plato(request, id):
    plato = get_object_or_404(Plato, id=id)
    insumos = Insumo.objects.filter(activo=True).order_by("nombre")
    ingredientes = RecetaDetalle.objects.filter(plato=plato).select_related("insumo")
    return render(request, "recetas/costeo.html", {"plato": plato, "insumos": insumos, "ingredientes": ingredientes})

def guardar_ingrediente_receta(request):
    if request.method == "POST":
        plato = get_object_or_404(Plato, id=request.POST["plato_id"])
        insumo = get_object_or_404(Insumo, id=request.POST["insumo_id"])

        RecetaDetalle.objects.update_or_create(
            plato=plato,
            insumo=insumo,
            defaults={"cantidad": request.POST["cantidad"]}
        )

        return redirect(f"/costeoPlato/{plato.id}/")

    return redirect("/platos/")

def eliminar_ingrediente_receta(request, id):
    ingrediente = get_object_or_404(RecetaDetalle, id=id)
    plato_id = ingrediente.plato.id

    if request.method == "POST":
        ingrediente.delete()

    return redirect(f"/costeoPlato/{plato_id}/")

#Ensamblar
def ensamblar_menu(request, id):
    menu = get_object_or_404(Menu, id=id)

    platos_menu = MenuPlato.objects.filter(
        menu=menu
    ).select_related("plato").order_by("tiempo_menu", "orden")

    platos_asignados = platos_menu.values_list("plato_id", flat=True)

    platos_disponibles = Plato.objects.filter(
        activo=True
    ).exclude(
        id__in=platos_asignados
    ).order_by("tiempo_menu", "nombre")

    zonas = [
        {
            "codigo": "ENTRADA",
            "nombre": "Entradas",
            "icono": "fas fa-utensils",
            "platos": platos_menu.filter(tiempo_menu="ENTRADA")
        },
        {
            "codigo": "PRINCIPAL",
            "nombre": "Platos principales",
            "icono": "fas fa-drumstick-bite",
            "platos": platos_menu.filter(tiempo_menu="PRINCIPAL")
        },
        {
            "codigo": "ACOMPANAMIENTO",
            "nombre": "Acompañamientos",
            "icono": "fas fa-bowl-food",
            "platos": platos_menu.filter(tiempo_menu="ACOMPANAMIENTO")
        },
        {
            "codigo": "POSTRE",
            "nombre": "Postres",
            "icono": "fas fa-ice-cream",
            "platos": platos_menu.filter(tiempo_menu="POSTRE")
        },
        {
            "codigo": "BEBIDA",
            "nombre": "Bebidas",
            "icono": "fas fa-glass-water",
            "platos": platos_menu.filter(tiempo_menu="BEBIDA")
        },
        {
            "codigo": "OTRO",
            "nombre": "Otros",
            "icono": "fas fa-ellipsis",
            "platos": platos_menu.filter(tiempo_menu="OTRO")
        }
    ]

    datos = {
        "menu": menu,
        "platos_disponibles": platos_disponibles,
        "zonas": zonas,
        "cantidad_platos": platos_menu.count()
    }

    return render(request, "menus/ensamblar.html", datos)

def agregar_plato_menu(request):
    if request.method == "POST":
        menu = get_object_or_404(Menu, id=request.POST["menu_id"])
        plato = get_object_or_404(Plato, id=request.POST["plato_id"])

        ultimo_plato = MenuPlato.objects.filter(
            menu=menu,
            tiempo_menu=plato.tiempo_menu
        ).order_by("-orden").first()

        if ultimo_plato:
            nuevo_orden = ultimo_plato.orden + 1
        else:
            nuevo_orden = 1

        menu_plato, creado = MenuPlato.objects.get_or_create(
            menu=menu,
            plato=plato,
            defaults={
                "tiempo_menu": plato.tiempo_menu,
                "orden": nuevo_orden,
                "cantidad_por_persona": 1
            }
        )

        if creado:
            return JsonResponse({
                "ok": True,
                "mensaje": "Plato agregado correctamente"
            })

        return JsonResponse({
            "ok": False,
            "mensaje": "Este plato ya pertenece al menú"
        })

    return JsonResponse({
        "ok": False,
        "mensaje": "Método no permitido"
    }, status=405)

def ordenar_platos_menu(request):
    if request.method == "POST":
        menu = get_object_or_404(Menu, id=request.POST["menu_id"])
        identificadores = request.POST.getlist("ids[]")

        for posicion, menu_plato_id in enumerate(identificadores, start=1):
            MenuPlato.objects.filter(
                id=menu_plato_id,
                menu=menu
            ).update(orden=posicion)

        return JsonResponse({
            "ok": True,
            "mensaje": "Orden actualizado"
        })

    return JsonResponse({
        "ok": False,
        "mensaje": "Método no permitido"
    }, status=405)

def eliminar_plato_menu(request, id):
    menu_plato = get_object_or_404(MenuPlato, id=id)
    menu_id = menu_plato.menu.id

    if request.method == "POST":
        menu_plato.delete()

    return redirect(f"/ensamblarMenu/{menu_id}/")

#Calendario
def calendario_eventos(request):
    return render(request, "eventos/calendario.html")

def datos_calendario(request):
    eventos = EventoCatering.objects.select_related("cliente", "menu").all().order_by("fecha_inicio")

    colores = {
        "COTIZADO": "#6c757d",
        "CONFIRMADO": "#0d6efd",
        "PREPARACION": "#fd7e14",
        "EN_CURSO": "#198754",
        "FINALIZADO": "#212529",
        "CANCELADO": "#dc3545",
    }

    datos = []

    for evento in eventos:
        color = colores.get(evento.estado, "#dc3545")

        datos.append({
            "id": evento.id,
            "title": evento.nombre_evento,
            "start": evento.fecha_inicio.isoformat(),
            "end": evento.fecha_fin.isoformat() if evento.fecha_fin else None,
            "backgroundColor": color,
            "borderColor": color,
            "textColor": "#ffffff",
            "extendedProps": {
                "cliente": evento.cliente.nombre,
                "menu": evento.menu.nombre if evento.menu else "Sin menú",
                "tipo_servicio": evento.get_tipo_servicio_display(),
                "estado": evento.get_estado_display(),
                "direccion": evento.direccion,
                "numero_personas": evento.numero_personas,
                "total_contratado": str(evento.total_contratado),
                "anticipo": str(evento.anticipo),
                "observaciones": evento.observaciones if evento.observaciones else "Sin observaciones",
            }
        })

    return JsonResponse(datos, safe=False)

# COCINEROS

def listado_cocineros(request):
    cocineros = Cocinero.objects.filter(activo=True).order_by("nombres")
    return render(request, "cocineros/listado.html", {"cocineros": cocineros})

def nuevo_cocinero(request):
    return render(request, "cocineros/formulario.html")

def guardar_cocinero(request):
    if request.method == "POST":
        Cocinero.objects.create(
            nombres=request.POST["nombres"],
            identificacion=request.POST["identificacion"],
            telefono=request.POST.get("telefono", ""),
            especialidad=request.POST.get("especialidad", ""),
            activo=request.POST.get("activo") == "on",
        )

    return redirect("/cocineros/")

def editar_cocinero(request, id):
    cocinero = get_object_or_404(Cocinero, id=id)
    return render(request, "cocineros/formulario.html", {"cocinero": cocinero})

def actualizar_cocinero(request, id):
    cocinero = get_object_or_404(Cocinero, id=id)

    if request.method == "POST":
        cocinero.nombres = request.POST["nombres"]
        cocinero.identificacion = request.POST["identificacion"]
        cocinero.telefono = request.POST.get("telefono", "")
        cocinero.especialidad = request.POST.get("especialidad", "")
        cocinero.activo = request.POST.get("activo") == "on"
        cocinero.save()

    return redirect("/cocineros/")

def eliminar_cocinero(request, id):
    cocinero = get_object_or_404(Cocinero, id=id)

    if request.method == "POST":
        cocinero.activo = False
        cocinero.save()

    return redirect("/cocineros/")

def asignar_cocineros(request, id):
    evento = get_object_or_404(EventoCatering, id=id)
    cocineros = list(Cocinero.objects.filter(activo=True).order_by("nombres"))
    asignaciones = {asignacion.cocinero_id: asignacion for asignacion in EventoCocinero.objects.filter(evento=evento)}

    for cocinero in cocineros:
        asignacion = asignaciones.get(cocinero.id)
        cocinero.seleccionado = asignacion is not None
        cocinero.rol_asignado = asignacion.rol if asignacion else "COCINERO"
        cocinero.horas_asignadas = asignacion.horas_asignadas if asignacion else 0

    return render(request, "eventos/asignar_cocineros.html", {"evento": evento, "cocineros": cocineros})

def guardar_cocineros_evento(request, id):
    evento = get_object_or_404(EventoCatering, id=id)

    if request.method == "POST":
        seleccionados = request.POST.getlist("cocinero_ids")
        EventoCocinero.objects.filter(evento=evento).exclude(cocinero_id__in=seleccionados).delete()

        for cocinero_id in seleccionados:
            cocinero = get_object_or_404(Cocinero, id=cocinero_id)
            EventoCocinero.objects.update_or_create(
                evento=evento,
                cocinero=cocinero,
                defaults={
                    "rol": request.POST.get(f"rol_{cocinero_id}", "COCINERO"),
                    "horas_asignadas": request.POST.get(f"horas_{cocinero_id}", "0"),
                }
            )

        messages.success(request, "Los cocineros fueron asignados correctamente.")

    return redirect(f"/asignarCocineros/{evento.id}/")

# UTILERÍA

def listado_utileria(request):
    utilerias = Utileria.objects.filter(activo=True).order_by("categoria", "nombre")
    return render(request, "utileria/listado.html", {"utilerias": utilerias})

def nueva_utileria(request):
    return render(request, "utileria/formulario.html")

def guardar_utileria(request):
    if request.method == "POST":
        Utileria.objects.create(
            nombre=request.POST["nombre"],
            categoria=request.POST["categoria"],
            cantidad_total=request.POST["cantidad_total"],
            costo_reposicion=request.POST["costo_reposicion"],
            descripcion=request.POST.get("descripcion", ""),
            activo=request.POST.get("activo") == "on",
        )

    return redirect("/utileria/")

def editar_utileria(request, id):
    utileria = get_object_or_404(Utileria, id=id)
    return render(request, "utileria/formulario.html", {"utileria": utileria})

def actualizar_utileria(request, id):
    utileria = get_object_or_404(Utileria, id=id)

    if request.method == "POST":
        utileria.nombre = request.POST["nombre"]
        utileria.categoria = request.POST["categoria"]
        utileria.cantidad_total = request.POST["cantidad_total"]
        utileria.costo_reposicion = request.POST["costo_reposicion"]
        utileria.descripcion = request.POST.get("descripcion", "")
        utileria.activo = request.POST.get("activo") == "on"
        utileria.save()

    return redirect("/utileria/")

def eliminar_utileria(request, id):
    utileria = get_object_or_404(Utileria, id=id)

    if request.method == "POST":
        utileria.activo = False
        utileria.save()

    return redirect("/utileria/")

def asignar_utileria(request, id):
    evento = get_object_or_404(EventoCatering, id=id)
    utilerias = list(Utileria.objects.filter(activo=True).order_by("categoria", "nombre"))
    asignaciones = EventoUtileria.objects.filter(evento=evento).select_related("utileria").order_by("utileria__nombre")

    for utileria in utilerias:
        reservada = EventoUtileria.objects.filter(utileria=utileria).exclude(evento=evento).exclude(estado="DEVUELTA").aggregate(total=Sum("cantidad"))["total"] or 0
        utileria.disponible = max(utileria.cantidad_total - reservada, 0)

    return render(request, "eventos/asignar_utileria.html", {"evento": evento, "utilerias": utilerias, "asignaciones": asignaciones})

def guardar_utileria_evento(request, id):
    evento = get_object_or_404(EventoCatering, id=id)

    if request.method == "POST":
        utileria = get_object_or_404(Utileria, id=request.POST["utileria_id"])
        cantidad = int(request.POST["cantidad"])
        reservada = EventoUtileria.objects.filter(utileria=utileria).exclude(evento=evento).exclude(estado="DEVUELTA").aggregate(total=Sum("cantidad"))["total"] or 0
        disponible = utileria.cantidad_total - reservada

        if cantidad > disponible:
            messages.error(request, f"Solo existen {disponible} unidades disponibles de {utileria.nombre}.")
        else:
            EventoUtileria.objects.update_or_create(
                evento=evento,
                utileria=utileria,
                defaults={
                    "cantidad": cantidad,
                    "estado": request.POST["estado"],
                    "cantidad_devuelta": request.POST.get("cantidad_devuelta", "0"),
                    "observaciones": request.POST.get("observaciones", ""),
                }
            )
            messages.success(request, "La utilería fue asignada correctamente.")

    return redirect(f"/asignarUtileria/{evento.id}/")

def eliminar_utileria_evento(request, id):
    asignacion = get_object_or_404(EventoUtileria, id=id)
    evento_id = asignacion.evento_id

    if request.method == "POST":
        asignacion.delete()

    return redirect(f"/asignarUtileria/{evento_id}/")

# ENTREGAS

def listado_entregas(request):
    entregas = Entrega.objects.select_related("evento", "responsable").order_by("fecha_salida")
    return render(request, "entregas/listado.html", {"entregas": entregas})

def nueva_entrega(request):
    eventos = EventoCatering.objects.exclude(estado__in=["FINALIZADO", "CANCELADO"]).order_by("fecha_inicio")
    responsables = User.objects.filter(is_active=True).order_by("first_name", "username")
    return render(request, "entregas/formulario.html", {"eventos": eventos, "responsables": responsables})

def guardar_entrega(request):
    if request.method == "POST":
        responsable_id = request.POST.get("responsable_id", "")
        responsable = User.objects.filter(id=responsable_id).first() if responsable_id else None
        fecha_entrega = request.POST.get("fecha_entrega", "") or None

        Entrega.objects.create(
            evento=get_object_or_404(EventoCatering, id=request.POST["evento_id"]),
            responsable=responsable,
            fecha_salida=request.POST["fecha_salida"],
            fecha_entrega=fecha_entrega,
            direccion_entrega=request.POST["direccion_entrega"],
            vehiculo=request.POST.get("vehiculo", ""),
            estado=request.POST["estado"],
            observaciones=request.POST.get("observaciones", ""),
        )

    return redirect("/entregas/")

def editar_entrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)
    eventos = EventoCatering.objects.order_by("fecha_inicio")
    responsables = User.objects.filter(is_active=True).order_by("first_name", "username")
    return render(request, "entregas/formulario.html", {"entrega": entrega, "eventos": eventos, "responsables": responsables})

def actualizar_entrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)

    if request.method == "POST":
        responsable_id = request.POST.get("responsable_id", "")
        entrega.evento = get_object_or_404(EventoCatering, id=request.POST["evento_id"])
        entrega.responsable = User.objects.filter(id=responsable_id).first() if responsable_id else None
        entrega.fecha_salida = request.POST["fecha_salida"]
        entrega.fecha_entrega = request.POST.get("fecha_entrega", "") or None
        entrega.direccion_entrega = request.POST["direccion_entrega"]
        entrega.vehiculo = request.POST.get("vehiculo", "")
        entrega.estado = request.POST["estado"]
        entrega.observaciones = request.POST.get("observaciones", "")
        entrega.save()

    return redirect("/entregas/")

def eliminar_entrega(request, id):
    entrega = get_object_or_404(Entrega, id=id)

    if request.method == "POST":
        entrega.delete()

    return redirect("/entregas/")

# COMANDAS Y HOTKEYS-JS

def listado_comandas(request):
    evento_id = request.GET.get("evento", "")
    comandas = Comanda.objects.select_related("evento").prefetch_related("detalles__plato")

    if evento_id:
        comandas = comandas.filter(evento_id=evento_id)

    eventos = EventoCatering.objects.order_by("-fecha_inicio")
    return render(request, "comandas/listado.html", {"comandas": comandas, "eventos": eventos, "evento_seleccionado": evento_id})

def nueva_comanda(request):
    eventos = EventoCatering.objects.exclude(estado__in=["FINALIZADO", "CANCELADO"]).order_by("fecha_inicio")
    platos = Plato.objects.filter(activo=True).order_by("tecla_rapida", "nombre")
    return render(request, "comandas/formulario.html", {"eventos": eventos, "platos": platos})

def guardar_comanda(request):
    if request.method == "POST":
        comanda = Comanda.objects.create(
            evento=get_object_or_404(EventoCatering, id=request.POST["evento_id"]),
            numero_mesa=request.POST.get("numero_mesa", "") or None,
            observaciones=request.POST.get("observaciones", ""),
        )

        total_detalles = 0
        for plato in Plato.objects.filter(activo=True):
            cantidad = int(request.POST.get(f"cantidad_{plato.id}", "0") or 0)

            if cantidad > 0:
                DetalleComanda.objects.create(comanda=comanda, plato=plato, cantidad=cantidad)
                total_detalles += 1

        if total_detalles == 0:
            comanda.delete()
            messages.error(request, "Debe agregar al menos un plato a la comanda.")
            return redirect("/nuevaComanda/")

        messages.success(request, f"La comanda {comanda.codigo} fue creada correctamente.")

    return redirect("/comandas/")

def actualizar_estado_comanda(request, id):
    comanda = get_object_or_404(Comanda, id=id)

    if request.method == "POST":
        estado = request.POST["estado"]
        estados_validos = [valor for valor, texto in Comanda.ESTADOS]

        if estado in estados_validos:
            comanda.estado = estado

            if estado == "DESPACHADA":
                comanda.fecha_despacho = timezone.now()

            comanda.save()

    return redirect("/comandas/")

def eliminar_comanda(request, id):
    comanda = get_object_or_404(Comanda, id=id)

    if request.method == "POST":
        comanda.delete()

    return redirect("/comandas/")

# REPORTES

def reporte_margenes(request):
    resultados = []

    for plato in Plato.objects.filter(activo=True).order_by("nombre"):
        costo = plato.costo_receta()
        margen = plato.precio_venta - costo
        porcentaje = (margen / plato.precio_venta) * 100 if plato.precio_venta else Decimal("0.00")
        resultados.append({
            "plato": plato,
            "costo": costo,
            "margen": margen,
            "porcentaje": porcentaje,
        })

    resultados.sort(key=lambda elemento: elemento["margen"], reverse=True)
    return render(request, "reportes/margenes.html", {"resultados": resultados})

def reporte_insumos_semanal(request):
    fecha_texto = request.GET.get("fecha", "")
    fecha_base = datetime.strptime(fecha_texto, "%Y-%m-%d").date() if fecha_texto else timezone.localdate()
    inicio_semana = fecha_base - timedelta(days=fecha_base.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_filtro = timezone.make_aware(datetime.combine(inicio_semana, datetime.min.time()))
    fin_filtro = inicio_filtro + timedelta(days=7)

    eventos = EventoCatering.objects.select_related("menu", "cliente").filter(
        fecha_inicio__gte=inicio_filtro,
        fecha_inicio__lt=fin_filtro,
        estado__in=["CONFIRMADO", "PREPARACION", "EN_CURSO"]
    ).order_by("fecha_inicio")

    requerimientos = {}

    for evento in eventos:
        detalles_menu = MenuPlato.objects.filter(menu=evento.menu).select_related("plato").prefetch_related("plato__ingredientes_receta__insumo")

        for detalle_menu in detalles_menu:
            for ingrediente in detalle_menu.plato.ingredientes_receta.all():
                cantidad = ingrediente.cantidad * detalle_menu.cantidad_por_persona * Decimal(evento.numero_personas)

                if ingrediente.insumo_id not in requerimientos:
                    requerimientos[ingrediente.insumo_id] = {
                        "insumo": ingrediente.insumo,
                        "cantidad_requerida": Decimal("0.000"),
                    }

                requerimientos[ingrediente.insumo_id]["cantidad_requerida"] += cantidad

    resultados = []

    for dato in requerimientos.values():
        stock = dato["insumo"].stock_actual
        compra = max(dato["cantidad_requerida"] - stock, Decimal("0.000"))
        resultados.append({
            "insumo": dato["insumo"],
            "cantidad_requerida": dato["cantidad_requerida"],
            "stock": stock,
            "cantidad_comprar": compra,
        })

    resultados.sort(key=lambda elemento: elemento["insumo"].nombre)

    contexto = {
        "fecha_consulta": inicio_semana.strftime("%Y-%m-%d"),
        "inicio_semana": inicio_semana,
        "fin_semana": fin_semana,
        "eventos": eventos,
        "resultados": resultados,
    }

    return render(request, "reportes/insumos_semanal.html", contexto)

# CANTIDAD DE PLATOS DENTRO DEL MENÚ

def actualizar_cantidad_menu_plato(request, id):
    detalle = get_object_or_404(MenuPlato, id=id)

    if request.method == "POST":
        detalle.cantidad_por_persona = request.POST["cantidad_por_persona"]
        detalle.save()

    return redirect(f"/ensamblarMenu/{detalle.menu_id}/")
