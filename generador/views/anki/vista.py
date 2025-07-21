from django.shortcuts import render, redirect
from django.utils import timezone
from .logica import preguntas_para_repasar, responder_pregunta, obtener_o_crear_repeticion
from generador.models import Pregunta, Tema, Repeticion
import random
from django.urls import reverse
from django.http import HttpResponseRedirect

def anki_view(request):
    temas = Tema.objects.all()
    tema_seleccionado = request.GET.get("tema") or request.POST.get("tema")
    ahora = timezone.now()

    repetidas = preguntas_para_repasar(tema_seleccionado)

    # Inicializar variables
    mensaje = None
    mostrar_explicacion = False
    respuesta_usuario = None

    if request.method == 'POST':
        pregunta_id = request.POST.get("pregunta_id")
        pregunta = Pregunta.objects.get(id=pregunta_id)
        alternativas = [
           ('A', pregunta.alternativa_a),
           ('B', pregunta.alternativa_b),
           ('C', pregunta.alternativa_c),
           ('D', pregunta.alternativa_d),
        ]


        # Si viene un nivel de dificultad, actualiza y pasa a siguiente pregunta
        if 'nivel' in request.POST:
            nivel = int(request.POST.get('nivel'))
            responder_pregunta(pregunta_id, nivel)
            return HttpResponseRedirect(f"{reverse('practicar')}?tema={tema_seleccionado}")

        # Si viene una respuesta A/B/C/D, evaluar
        respuesta_usuario = request.POST.get("respuesta")
        correcta = (respuesta_usuario == pregunta.respuesta_correcta)
        mensaje = "✅ ¡Correcto!" if correcta else f"❌ Incorrecto. La respuesta correcta era {pregunta.respuesta_correcta}"
        mostrar_explicacion = True

        # Trae la repetición activa para esa pregunta
        repeticion = obtener_o_crear_repeticion(pregunta)

        return render(request, "practicar.html", {
               "temas": temas,
               "tema_seleccionado": tema_seleccionado,
               "repeticion": repeticion,
               "alternativas": alternativas,
               "pregunta_resuelta": True,
               "respuesta_usuario": respuesta_usuario,
               "mostrar_explicacion": mostrar_explicacion,
               "mensaje": mensaje,
               })


    # Mostrar siguiente pregunta
    if repetidas.exists():
        repeticion = repetidas.first()
    else:
        ya_registradas = Repeticion.objects.values_list('pregunta_id', flat=True)
        nuevas = Pregunta.objects.exclude(id__in=ya_registradas)
        if tema_seleccionado:
            nuevas = nuevas.filter(tema__nombre=tema_seleccionado)
        if nuevas.exists():
            pregunta = random.choice(list(nuevas))
            repeticion = Repeticion.objects.create(pregunta=pregunta)
        else:
            return render(request, 'terminado.html', {
                'temas': temas,
                'tema_seleccionado': tema_seleccionado
            })


    alternativas = [
        ('A', repeticion.pregunta.alternativa_a),
        ('B', repeticion.pregunta.alternativa_b),
        ('C', repeticion.pregunta.alternativa_c),
        ('D', repeticion.pregunta.alternativa_d),
    ]
    return render(request, "practicar.html", {
    "temas": temas,
    "tema_seleccionado": tema_seleccionado,
    "repeticion": repeticion,
    "alternativas": alternativas,
    "pregunta_resuelta": True,
    "respuesta_usuario": respuesta_usuario,
    "mostrar_explicacion": mostrar_explicacion,
    "mensaje": mensaje,
})

