from django.utils import timezone
from generador.models import Pregunta, Repeticion

# Devuelve preguntas pendientes de revisar ordenadas por prioridad (más urgente primero)
def preguntas_para_repasar(tema_nombre=None):
    ahora = timezone.now()
    repetidas = Repeticion.objects.filter(proxima_repeticion__lte=ahora)
    if tema_nombre:
        repetidas = repetidas.filter(pregunta__tema__nombre=tema_nombre)
    return repetidas.order_by('proxima_repeticion')

# Crea una repetición si no existe
def obtener_o_crear_repeticion(pregunta):
    repeticion, creada = Repeticion.objects.get_or_create(
        pregunta=pregunta,
        defaults={'proxima_repeticion': timezone.now()}
    )
    return repeticion

# Registra respuesta con el nivel (0=Incorrecta, 1=Difícil, 2=Bien, 3=Fácil)
def responder_pregunta(pregunta_id, nivel_respuesta):
    try:
        pregunta = Pregunta.objects.get(id=pregunta_id)
        repeticion = obtener_o_crear_repeticion(pregunta)
        repeticion.actualizar_repeticion(nivel_respuesta)
        return True
    except Pregunta.DoesNotExist:
        return False