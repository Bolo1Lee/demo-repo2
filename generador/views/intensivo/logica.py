# generador/views/intensivo/logica.py

from django.utils import timezone
from generador.models import Pregunta, Repeticion
from datetime import timedelta

# Devuelve preguntas pendientes de revisar en modo intensivo
def preguntas_para_repasar_intensivo(usuario, tema_nombre=None):
    ahora = timezone.now()
    repetidas = Repeticion.objects.filter(
        proxima_repeticion__lte=ahora,
        pregunta__usuario=usuario,
        modo="intensivo"
    )
    if tema_nombre:
        repetidas = repetidas.filter(pregunta__tema__nombre=tema_nombre)
    return repetidas.order_by('proxima_repeticion')

# Crea una repetición intensiva si no existe
def obtener_o_crear_repeticion_intensiva(pregunta):
    repeticion, creada = Repeticion.objects.get_or_create(
        pregunta=pregunta,
        modo="intensivo",
        defaults={
            'proxima_repeticion': timezone.now(),
            'stability': 1.0,
            'difficulty': 0.3,
            'interval': 0.0,
            'lapses': 0,
        }
    )
    return repeticion

# Respuesta intensiva
def responder_pregunta_intensiva(pregunta_id, nivel_respuesta):
    try:
        pregunta = Pregunta.objects.get(id=pregunta_id)
        repeticion = obtener_o_crear_repeticion_intensiva(pregunta)

        ahora = timezone.now()
        if nivel_respuesta == 0:  # Incorrecta
            intervalo = timedelta(minutes=10)
        elif nivel_respuesta == 1:  # Difícil
            intervalo = timedelta(minutes=30)
        elif nivel_respuesta == 2:  # Bien
            intervalo = timedelta(hours=1)
        elif nivel_respuesta == 3:  # Fácil
            intervalo = timedelta(hours=6)
        else:
            intervalo = timedelta(hours=1)  # fallback

        repeticion.proxima_repeticion = ahora + intervalo
        repeticion.nivel_respuesta = nivel_respuesta
        repeticion.fecha_ultima_respuesta = ahora
        repeticion.save()
        return True
    except Pregunta.DoesNotExist:
        return False
