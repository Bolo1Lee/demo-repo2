from django.shortcuts import render, redirect
from django.utils import timezone
from generador.models import Pregunta, Tema, Repeticion
from .logica import (
    preguntas_para_repasar_intensivo,
    obtener_o_crear_repeticion_intensiva,
    responder_pregunta_intensiva,
)
import random
from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import timedelta

def obtener_estadisticas_intensivo(usuario, tema_nombre=None):
    ahora = timezone.now()
    hoy = ahora.date()

    tarjetas_nuevas = Pregunta.objects.filter(usuario=usuario).exclude(repeticion__modo="intensivo")
    tarjetas_repasar = Repeticion.objects.filter(pregunta__usuario=usuario, modo="intensivo", proxima_repeticion__lte=ahora)
    tarjetas_estudiadas_hoy = Repeticion.objects.filter(pregunta__usuario=usuario, modo="intensivo", fecha_ultima_respuesta__date=hoy)

    if tema_nombre:
        tarjetas_nuevas = tarjetas_nuevas.filter(tema__nombre=tema_nombre)
        tarjetas_repasar = tarjetas_repasar.filter(pregunta__tema__nombre=tema_nombre)
        tarjetas_estudiadas_hoy = tarjetas_estudiadas_hoy.filter(pregunta__tema__nombre=tema_nombre)

    return {
        "tarjetas_nuevas": tarjetas_nuevas.count(),
        "tarjetas_para_repasar": tarjetas_repasar.count(),
        "total_estudiadas": tarjetas_estudiadas_hoy.count(),
    }

def intensivo_view(request):
    temas = Tema.objects.all()
    tema_seleccionado = request.GET.get("tema") or request.POST.get("tema")
    ahora = timezone.now()

    estadisticas = obtener_estadisticas_intensivo(request.user, tema_seleccionado)
    repetidas = preguntas_para_repasar_intensivo(request.user, tema_seleccionado)

    mensaje = None
    mostrar_explicacion = False
    respuesta_usuario = None

    # Nivel, texto, clase, duración
    niveles_textos = [
        (0, "Incorrecta", "bg-red-500", timedelta(minutes=10)),
        (1, "Difícil", "bg-yellow-500", timedelta(minutes=30)),
        (2, "Bien", "bg-blue-500", timedelta(hours=1)),
        (3, "Fácil", "bg-green-600", timedelta(hours=6)),
    ]

    repeticion_preview = {
        nivel: {
            "intervalo": f"{int(duracion.total_seconds() // 60)} min" if duracion < timedelta(hours=1) else f"{int(duracion.total_seconds() // 3600)} h",
            "fecha": ahora + duracion
        }
        for nivel, _, _, duracion in niveles_textos
    }

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
            responder_pregunta_intensiva(pregunta_id, nivel)
            return HttpResponseRedirect(f"{reverse('intensivo')}?tema={tema_seleccionado}")

        respuesta_usuario = request.POST.get("respuesta")
        correcta = (respuesta_usuario == pregunta.respuesta_correcta)
        mensaje = "✅ ¡Correcto!" if correcta else f"❌ Incorrecto. La respuesta correcta era {pregunta.respuesta_correcta}"
        mostrar_explicacion = True

        repeticion = obtener_o_crear_repeticion_intensiva(pregunta)

        return render(request, "intensivo.html", {
            "temas": temas,
            "tema_seleccionado": tema_seleccionado,
            "repeticion": repeticion,
            "alternativas": alternativas,
            "pregunta_resuelta": True,
            "respuesta_usuario": respuesta_usuario,
            "mostrar_explicacion": mostrar_explicacion,
            "mensaje": mensaje,
            "niveles_textos": [(nivel, texto, clase) for nivel, texto, clase, _ in niveles_textos],
            "repeticion_preview": repeticion_preview,
            "tarjetas_nuevas": estadisticas["tarjetas_nuevas"],
            "tarjetas_para_repasar": estadisticas["tarjetas_para_repasar"],
            "total_estudiadas": estadisticas["total_estudiadas"],
        })

    if repetidas.exists():
        repeticion = repetidas.first()
    else:
        ya_registradas = Repeticion.objects.filter(modo="intensivo").values_list('pregunta_id', flat=True)
        nuevas = Pregunta.objects.filter(usuario=request.user).exclude(id__in=ya_registradas)
        if tema_seleccionado:
            nuevas = nuevas.filter(tema__nombre=tema_seleccionado)
        if nuevas.exists():
            pregunta = random.choice(list(nuevas))
            repeticion = Repeticion.objects.create(pregunta=pregunta, modo="intensivo")
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

    return render(request, "intensivo.html", {
        "temas": temas,
        "tema_seleccionado": tema_seleccionado,
        "repeticion": repeticion,
        "alternativas": alternativas,
        "pregunta_resuelta": True,
        "respuesta_usuario": respuesta_usuario,
        "mostrar_explicacion": mostrar_explicacion,
        "mensaje": mensaje,
        "niveles_textos": [(nivel, texto, clase) for nivel, texto, clase, _ in niveles_textos],
        "repeticion_preview": repeticion_preview,
        "tarjetas_nuevas": estadisticas["tarjetas_nuevas"],
        "tarjetas_para_repasar": estadisticas["tarjetas_para_repasar"],
        "total_estudiadas": estadisticas["total_estudiadas"],
    })
