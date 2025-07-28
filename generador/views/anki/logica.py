from django.utils import timezone
from generador.models import Pregunta, Repeticion

# Devuelve preguntas pendientes de revisar ordenadas por prioridad (más urgente primero)
def preguntas_para_repasar(usuario, tema_nombre=None):
    ahora = timezone.now()
    repetidas = Repeticion.objects.filter(
        proxima_repeticion__lte=ahora,
        pregunta__usuario=usuario
    )
    if tema_nombre:
        repetidas = repetidas.filter(pregunta__tema__nombre=tema_nombre)
    return repetidas.order_by('proxima_repeticion')

# Crea una repetición si no existe
def obtener_o_crear_repeticion(pregunta):
    repeticion, creada = Repeticion.objects.get_or_create(
        pregunta=pregunta,
        defaults={
            'proxima_repeticion': timezone.now(),
            'stability': 1.0,
            'difficulty': 0.3,
            'interval': 0.0,
            'lapses': 0,
        }
    )
    return repeticion


# Registra respuesta con el nivel (0=Incorrecta, 1=Difícil, 2=Bien, 3=Fácil)
def responder_pregunta(pregunta_id, nivel_respuesta):
    try:
        pregunta = Pregunta.objects.get(id=pregunta_id)
        repeticion = obtener_o_crear_repeticion(pregunta)
        repeticion.actualizar_repeticion(nivel_respuesta)
        repeticion.fecha_ultima_respuesta = timezone.now()  # <--- NUEVO
        repeticion.save()
        return True
    except Pregunta.DoesNotExist:
        return False
    

def obtener_estadisticas_anki(usuario, tema_nombre=None):
    ahora = timezone.now()
    hoy = ahora.date()

    tarjetas_nuevas = Pregunta.objects.filter(usuario=usuario, repeticion__isnull=True)
    tarjetas_repasar = Repeticion.objects.filter(pregunta__usuario=usuario, proxima_repeticion__lte=ahora)
    tarjetas_estudiadas_hoy = Repeticion.objects.filter(pregunta__usuario=usuario, fecha_ultima_respuesta__date=hoy)

    if tema_nombre:
        tarjetas_nuevas = tarjetas_nuevas.filter(tema__nombre=tema_nombre)
        tarjetas_repasar = tarjetas_repasar.filter(pregunta__tema__nombre=tema_nombre)
        tarjetas_estudiadas_hoy = tarjetas_estudiadas_hoy.filter(pregunta__tema__nombre=tema_nombre)

    return {
        "tarjetas_nuevas": tarjetas_nuevas.count(),
        "tarjetas_para_repasar": tarjetas_repasar.count(),
        "total_estudiadas": tarjetas_estudiadas_hoy.count(),
    }

