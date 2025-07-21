from django.shortcuts import render
from generador.models import Pregunta, Tema
import random
from django.contrib.auth.decorators import login_required

@login_required
def practicar(request):
    temas = Tema.objects.all()
    tema_seleccionado = request.GET.get("tema", "")
    pregunta = None
    mensaje = ""
    mostrar_explicacion = False

    if tema_seleccionado:
        preguntas_tema = Pregunta.objects.filter(tema__nombre=tema_seleccionado)
        if preguntas_tema.exists():
            pregunta = random.choice(list(preguntas_tema))

    if request.method == "POST":
        pregunta_id = int(request.POST.get("pregunta_id"))
        respuesta_usuario = request.POST.get("respuesta")
        pregunta = Pregunta.objects.get(id=pregunta_id)
        mostrar_explicacion = True

        if respuesta_usuario == pregunta.respuesta_correcta:
            mensaje = "✅ ¡Correcto!"
        else:
            mensaje = f"❌ Incorrecto. La respuesta correcta era: {pregunta.respuesta_correcta}"

    return render(request, "practicar.html", {
        "temas": temas,
        "pregunta": pregunta,
        "mensaje": mensaje,
        "mostrar_explicacion": mostrar_explicacion,
        "tema_seleccionado": tema_seleccionado,
    })
