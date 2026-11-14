from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import RegistroForm, TareaForms
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from .models import Tarea, Proyecto, Categoria, Usuario
from django.contrib.auth.models import Group

def index(request):
    return render(request, 'index.html', {})

def registrar_usuario(request):
    if request.method == 'POST':
        formulario = RegistroForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()

            grupo, creado = Group.objects.get_or_create(name='Usuario')
            user.groups.add(grupo)

            login(request, user)
            return redirect('index')
    else:
        formulario = RegistroForm()

    return render(request, 'registration/signup.html', {'formulario': formulario})

@login_required
@permission_required('app.view_tarea')
def listar_tarea(request):
    tarea = Tarea.objects.filter(usuario_id=request.user.id)
    buscar = request.GET.get("buscar")
    estado = request.GET.get("estado")
    prioridad = request.GET.get("prioridad")
    proyecto = request.GET.get("proyecto")
    proyectos = Proyecto.objects.filter(usuario=request.user)
    categoria = request.GET.get("categoria")
    categorias = Categoria.objects.filter(usuario=request.user)
    orden = request.GET.get("orden")

    if buscar:
        tarea = tarea.filter(titulo__icontains=buscar)
    if estado:
        tarea = tarea.filter(estado=estado)
    if prioridad:
        tarea = tarea.filter(prioridad=prioridad)
    if proyecto:
        tarea = tarea.filter(proyecto_id=proyecto)
    if categoria:
        tarea = tarea.filter(categoria_id=categoria)
    if orden:
        if orden == "recientes":
            tarea = tarea.order_by('fecha_creacion')
        elif orden == "antiguas":
            tarea = tarea.order_by('-fecha_creacion')
        elif orden == "vencimiento":
            tarea = tarea.order_by('fecha_vencimiento')
        elif orden == "prioridad_alta":
            tarea = tarea.order_by('prioridad')
        elif orden == "prioridad_baja":
            tarea = tarea.order_by('-prioridad')
        elif orden == "az":
            tarea = tarea.order_by('titulo')
        elif orden == "za":
            tarea = tarea.order_by('-titulo')
    else:
        tarea = tarea.order_by('-fecha_creacion')

    return render(request, 'tarea/lista_tarea.html', {
        'tareas': tarea,
        'proyectos': proyectos,
        'categorias': categorias,
    })


@login_required
@permission_required('app.add_tarea')
def crear_tarea(request):
    if request.method == 'POST':
        formulario = TareaForms(request.POST)
        if formulario.is_valid():
            tarea = Tarea.objects.create(
                titulo=formulario.cleaned_data.get('titulo'),
                descripcion=formulario.cleaned_data.get('descripcion'),
                estado=formulario.cleaned_data.get('estado'),
                prioridad=formulario.cleaned_data.get('prioridad'),
                fecha_vencimiento=formulario.cleaned_data.get('fecha_vencimiento'),
                usuario_id=request.user.id
            )
            tarea.save()
            messages.success(request, "Tarea creada perfectamente")
            return redirect('lista_tarea')
    else:
        formulario = TareaForms()
    return render(request, 'tarea/crear_tarea.html', {'formulario': formulario})


@login_required
@permission_required('app.delete_tarea')
def eliminar_tarea(request, id_tarea):
    tarea = Tarea.objects.get(id=id_tarea, usuario_id=request.user.id)

    try:
        tarea.delete()
        messages.success(request, "Se ha eliminado la tarea correctamente.")
    except Exception as error:
        print(error)

    return redirect('lista_tarea')


@login_required
@permission_required('app.change_tarea')
def editar_tarea(request, id_tarea):
    tarea = Tarea.objects.get(id=id_tarea, usuario_id=request.user.id)

    if request.method == "POST":
        formulario = TareaForms(request.POST, instance=tarea)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Se ha modificado la tarea correctamente')
            return redirect('lista_tarea')
    else:
        formulario = TareaForms(instance=tarea)

    return render(request, 'tarea/editar_tarea.html', {'formulario': formulario, 'tarea': tarea})

from django.http import JsonResponse
from django.db.models import Q


@login_required
@permission_required('app.view_tarea')
def buscar_tarea(request):
    buscar = request.GET.get("buscar", "")

    tareas = Tarea.objects.filter(usuario=request.user).filter(
        Q(titulo__icontains=buscar)
    )

    resultados = []

    for tarea in tareas:
        resultados.append({
            "id": tarea.id,
            "titulo": tarea.titulo,
            "descripcion": tarea.descripcion,
            "estado": tarea.estado,
            "prioridad": tarea.prioridad,
            "fecha_vencimiento": tarea.fecha_vencimiento.strftime("%d/%m/%Y") if tarea.fecha_vencimiento else None,
            "completada": tarea.completada,
            "proyecto": {
                "id": tarea.proyecto.id,
                "nombre": tarea.proyecto.nombre,
            } if tarea.proyecto else None,
            "categoria": {
                "id": tarea.categoria.id,
                "nombre": tarea.categoria.nombre,
                "descripcion": tarea.categoria.descripcion,
            } if tarea.categoria else None,
        })

    return JsonResponse(resultados, safe=False)


