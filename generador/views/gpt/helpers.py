import json
import re
from generador.models import Pregunta

import json
import re
from generador.models import Pregunta

def limpiar_preguntas_json(respuesta_raw):
    """
    Limpia formato Markdown (```json ... ```) si es necesario y parsea el JSON.
    Soporta respuestas con o sin bloques ``` y devuelve una lista de preguntas válidas.
    """
    # Eliminar triple backticks y etiqueta opcional `json`
    respuesta_raw = re.sub(r"^```(?:json)?\s*", "", respuesta_raw.strip(), flags=re.IGNORECASE)
    respuesta_raw = re.sub(r"\s*```$", "", respuesta_raw.strip())

    try:
        preguntas = json.loads(respuesta_raw)
        if not isinstance(preguntas, list):
            raise ValueError("El JSON no contiene una lista de preguntas.")
        return preguntas
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear JSON: {str(e)}")


def es_pregunta_duplicada(nueva_pregunta, preguntas_existentes):
    """
    Compara el enunciado de la nueva pregunta con las ya guardadas en base de datos.
    """
    enunciado_raw = nueva_pregunta["pregunta"]

    # Asegurar que sea string
    if isinstance(enunciado_raw, list):
        enunciado = " ".join(enunciado_raw).strip().lower()
    elif isinstance(enunciado_raw, str):
        enunciado = enunciado_raw.strip().lower()
    else:
        enunciado = str(enunciado_raw).strip().lower()

    for p in preguntas_existentes:
        if enunciado == p.pregunta.strip().lower():
            return True
    return False


def guardar_preguntas(preguntas, tema):
    """
    Guarda las preguntas en la base de datos si no están repetidas y tienen al menos 4 alternativas.
    Devuelve una lista de preguntas guardadas y una lista de descartadas.
    """
    guardadas = []
    descartadas = []
    existentes = Pregunta.objects.filter(tema=tema)

    for item in preguntas:
        alternativas = item.get("alternativas", [])
        if len(alternativas) < 4:
            descartadas.append({"razon": "Menos de 4 alternativas", "contenido": item})
            continue

        # Normalizar enunciado
        enunciado_raw = item.get("pregunta", "")
        if isinstance(enunciado_raw, list):
            enunciado = " ".join(enunciado_raw).strip()
        elif isinstance(enunciado_raw, str):
            enunciado = enunciado_raw.strip()
        else:
            enunciado = str(enunciado_raw).strip()

        # Verificar duplicado
        if es_pregunta_duplicada({"pregunta": enunciado}, existentes):
            descartadas.append({"razon": "Duplicada", "contenido": item})
            continue

        nueva = Pregunta(
            pregunta=enunciado,
            alternativa_a=alternativas[0],
            alternativa_b=alternativas[1],
            alternativa_c=alternativas[2],
            alternativa_d=alternativas[3],
            respuesta_correcta=item["respuesta_correcta"],
            explicacion=item["explicacion"],
            tema=tema
        )
        nueva.save()
        guardadas.append(nueva)

    return guardadas, descartadas
