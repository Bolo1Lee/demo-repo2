from django.shortcuts import render, get_object_or_404, redirect
from generador.models import Pregunta, Tema
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
def lista_preguntas(request):
    tema_id = request.GET.get("tema", "")
    q = request.GET.get("q", "")

    preguntas = Pregunta.objects.filter(usuario=request.user).select_related('tema')

    if tema_id:
        preguntas = preguntas.filter(tema_id=tema_id)
    if q:
        preguntas = preguntas.filter(pregunta__icontains=q)

    temas = Tema.objects.filter(usuario=request.user)

    return render(request, "lista_preguntas.html", {
        "preguntas": preguntas,
        "temas": temas,
        "tema_filtrado": tema_id,
        "busqueda_actual": q
    })


@login_required
def editar_pregunta(request, pregunta_id):
    pregunta = get_object_or_404(Pregunta, id=pregunta_id, usuario=request.user)
    temas = Tema.objects.filter(usuario=request.user)
    errores = []

    if request.method == "POST":
        pregunta_texto = request.POST.get("pregunta", "")
        alternativa_a = request.POST.get("alternativa_a", "")
        alternativa_b = request.POST.get("alternativa_b", "")
        alternativa_c = request.POST.get("alternativa_c", "")
        alternativa_d = request.POST.get("alternativa_d", "")
        respuesta_correcta = request.POST.get("respuesta_correcta", "")
        explicacion = request.POST.get("explicacion", "")
        tema_id = request.POST.get("tema")

        if not pregunta_texto.strip():
            errores.append("La pregunta no puede estar vacía.")
        if respuesta_correcta not in ["A", "B", "C", "D"]:
            errores.append("La respuesta correcta debe ser A, B, C o D.")
        if not alternativa_a or not alternativa_b or not alternativa_c or not alternativa_d:
            errores.append("Todas las alternativas deben estar completas.")
        if not explicacion.strip():
            errores.append("La explicación no puede estar vacía.")
        if not tema_id:
            errores.append("Debes seleccionar un tema.")

        if not errores:
            pregunta.pregunta = pregunta_texto
            pregunta.alternativa_a = alternativa_a
            pregunta.alternativa_b = alternativa_b
            pregunta.alternativa_c = alternativa_c
            pregunta.alternativa_d = alternativa_d
            pregunta.respuesta_correcta = respuesta_correcta
            pregunta.explicacion = explicacion
            pregunta.tema = Tema.objects.get(id=tema_id)
            pregunta.save()
            return redirect("lista_preguntas")

    return render(request, "editar_pregunta.html", {
        "pregunta": pregunta,
        "temas": temas,
        "errores": errores
    })


@login_required
def eliminar_pregunta(request, pregunta_id):
    if request.method == "POST":
        pregunta = get_object_or_404(Pregunta, id=pregunta_id, usuario=request.user)
        pregunta.delete()
    return redirect("lista_preguntas")


@login_required
@require_POST
def eliminar_preguntas_multiples(request):
    ids = request.POST.getlist("preguntas_seleccionadas")
    if ids:
        preguntas = Pregunta.objects.filter(id__in=ids, usuario=request.user)
        eliminadas = preguntas.count()
        preguntas.delete()
        messages.success(request, f"Se eliminaron {eliminadas} preguntas.")
    else:
        messages.warning(request, "No seleccionaste ninguna pregunta.")
    return redirect("lista_preguntas")
