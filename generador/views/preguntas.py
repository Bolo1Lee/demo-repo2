from django.shortcuts import render, get_object_or_404, redirect
from generador.models import Pregunta, Tema

from django.contrib.auth.decorators import login_required

@login_required
def lista_preguntas(request):
    tema = request.GET.get("tema", "")
    q = request.GET.get("q", "")

    preguntas = Pregunta.objects.all().select_related('tema')

    if tema:
        preguntas = preguntas.filter(tema__nombre=tema)
    if q:
        preguntas = preguntas.filter(pregunta__icontains=q)

    temas = Tema.objects.all()

    return render(request, "lista_preguntas.html", {
        "preguntas": preguntas,
        "temas": temas,
        "tema_seleccionado": tema,
        "busqueda_actual": q
    })


def editar_pregunta(request, pregunta_id):
    pregunta = get_object_or_404(Pregunta, id=pregunta_id)
    temas = Tema.objects.all()
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
