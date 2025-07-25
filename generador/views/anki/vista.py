from django.shortcuts import render, redirect
from django.utils import timezone
from .logica import preguntas_para_repasar, responder_pregunta, obtener_o_crear_repeticion, obtener_estadisticas_anki
from generador.models import Pregunta, Tema, Repeticion
import random
from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import timedelta
import math

def calcular_fsrs_preview(repeticion, nivel):
    alpha = 0.4
    beta = 0.3
    gamma = 0.05
    delta = 0.05
    theta = 1
    target_retrievability = 0.9

    estabilidad = repeticion.stability
    dificultad = repeticion.difficulty
    ahora = timezone.now()

    if repeticion.fecha_ultima_respuesta:
        t = max((ahora - repeticion.fecha_ultima_respuesta).days, 0.01)
    else:
        t = 0.01

    r = math.exp(-theta * t / estabilidad)

    if nivel == 0:
        nueva_estabilidad = estabilidad * (1 - beta * r * dificultad)
        nueva_dificultad = min(1.0, dificultad + delta * r)
    else:
        nueva_estabilidad = estabilidad * (1 + alpha * (1 - r) * (1 - dificultad))
        nueva_dificultad = max(0.0, dificultad - gamma * (1 - r))

    nuevo_intervalo = nueva_estabilidad * math.log(1 / (1 - target_retrievability))
    fecha_proxima = ahora + timedelta(days=nuevo_intervalo)

    return round(nuevo_intervalo, 2), fecha_proxima


def anki_view(request):
    temas = Tema.objects.all()
    tema_seleccionado = request.GET.get("tema") or request.POST.get("tema")
    ahora = timezone.now()

    estadisticas = obtener_estadisticas_anki(tema_seleccionado)
    repetidas = preguntas_para_repasar(tema_seleccionado)

    mensaje = None
    mostrar_explicacion = False
    respuesta_usuario = None

    niveles_textos = [
        (0, "Incorrecta", "bg-red-500"),
        (1, "Difícil", "bg-yellow-500"),
        (2, "Bien", "bg-blue-500"),
        (3, "Fácil", "bg-green-600"),
    ]

    if request.method == 'POST':
        pregunta_id = request.POST.get("pregunta_id")
        pregunta = Pregunta.objects.get(id=pregunta_id)
        alternativas = [
            ('A', pregunta.alternativa_a),
            ('B', pregunta.alternativa_b),
            ('C', pregunta.alternativa_c),
            ('D', pregunta.alternativa_d),
        ]

        if 'nivel' in request.POST:
            nivel = int(request.POST.get('nivel'))
            responder_pregunta(pregunta_id, nivel)
            return HttpResponseRedirect(f"{reverse('practicar')}?tema={tema_seleccionado}")

        respuesta_usuario = request.POST.get("respuesta")
        correcta = (respuesta_usuario == pregunta.respuesta_correcta)
        mensaje = "✅ ¡Correcto!" if correcta else f"❌ Incorrecto. La respuesta correcta era {pregunta.respuesta_correcta}"
        mostrar_explicacion = True

        repeticion = obtener_o_crear_repeticion(pregunta)

        fsrs_preview = {
            i: {"intervalo": intervalo, "fecha": fecha}
            for i, (intervalo, fecha) in enumerate([
                calcular_fsrs_preview(repeticion, 0),
                calcular_fsrs_preview(repeticion, 1),
                calcular_fsrs_preview(repeticion, 2),
                calcular_fsrs_preview(repeticion, 3),
            ])
        }

        return render(request, "practicar.html", {
            "temas": temas,
            "tema_seleccionado": tema_seleccionado,
            "repeticion": repeticion,
            "alternativas": alternativas,
            "pregunta_resuelta": True,
            "respuesta_usuario": respuesta_usuario,
            "mostrar_explicacion": mostrar_explicacion,
            "mensaje": mensaje,
            "tarjetas_nuevas": estadisticas["tarjetas_nuevas"],
            "tarjetas_para_repasar": estadisticas["tarjetas_para_repasar"],
            "total_estudiadas": estadisticas["total_estudiadas"],
            "fsrs_preview": fsrs_preview,
            "niveles_textos": niveles_textos,
        })

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
                'tema_seleccionado': tema_seleccionado,
                "tarjetas_nuevas": estadisticas["tarjetas_nuevas"],
                "tarjetas_para_repasar": estadisticas["tarjetas_para_repasar"],
                "total_estudiadas": estadisticas["total_estudiadas"],
            })

    alternativas = [
        ('A', repeticion.pregunta.alternativa_a),
        ('B', repeticion.pregunta.alternativa_b),
        ('C', repeticion.pregunta.alternativa_c),
        ('D', repeticion.pregunta.alternativa_d),
    ]

    fsrs_preview = {
        i: {"intervalo": intervalo, "fecha": fecha}
        for i, (intervalo, fecha) in enumerate([
            calcular_fsrs_preview(repeticion, 0),
            calcular_fsrs_preview(repeticion, 1),
            calcular_fsrs_preview(repeticion, 2),
            calcular_fsrs_preview(repeticion, 3),
        ])
    }

    return render(request, "practicar.html", {
        "temas": temas,
        "tema_seleccionado": tema_seleccionado,
        "repeticion": repeticion,
        "alternativas": alternativas,
        "pregunta_resuelta": True,
        "respuesta_usuario": respuesta_usuario,
        "mostrar_explicacion": mostrar_explicacion,
        "mensaje": mensaje,
        "tarjetas_nuevas": estadisticas["tarjetas_nuevas"],
        "tarjetas_para_repasar": estadisticas["tarjetas_para_repasar"],
        "total_estudiadas": estadisticas["total_estudiadas"],
        "fsrs_preview": fsrs_preview,
        "niveles_textos": niveles_textos,
    })
