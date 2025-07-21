# generador/views/gpt/prompts.py

def generar_prompt(texto_usuario: str, tipo: str = "clinica") -> str:
    if tipo == "clinica":
        instrucciones = """
Eres un generador de preguntas de opción múltiple para estudiantes de medicina. A partir del siguiente texto, genera preguntas que cumplan los siguientes criterios:

- Están dirigidas a estudiantes clínicos avanzados.
- Evalúan aplicación de conocimientos en contextos clínicos (no memorización).
- Cada pregunta debe tener un breve caso clínico o situación médica concreta.
- Solo una alternativa es correcta.
- Las otras alternativas deben ser plausibles, pero incorrectas.
- Debe incluir una breve justificación explicando por qué la respuesta correcta lo es.

FORMATO ESTRICTO (JSON):

[
  {
    "pregunta": "Mujer de 65 años con DM2 consulta por dolor torácico súbito. ¿Cuál es el siguiente paso más adecuado?",
    "alternativas": ["A. ECG de control", "B. Medir troponinas", "C. Administrar AINEs", "D. Observación ambulatoria"],
    "respuesta_correcta": "B",
    "explicacion": "El dolor torácico súbito en paciente con riesgo cardiovascular debe ser evaluado inicialmente con marcadores de daño miocárdico como troponinas."
  }
]
"""
    elif tipo == "conceptual":
        instrucciones = """
Eres un generador de preguntas de opción múltiple para estudiantes de medicina. A partir del siguiente texto, genera preguntas que cumplan los siguientes criterios:

- Están dirigidas a estudiantes de medicina en formación.
- Evalúan la comprensión de conceptos clave, no resolución de casos clínicos.
- Cada pregunta debe tener una única alternativa correcta y cuatro en total.
- Debe incluir una justificación breve que explique por qué la respuesta es correcta.

FORMATO ESTRICTO (JSON):

[
  {
    "pregunta": "¿Cuál es el mecanismo de acción de la warfarina?",
    "alternativas": ["A. Inhibe la síntesis de prostaglandinas", "B. Antagoniza la vitamina K", "C. Bloquea canales de calcio", "D. Estimula la trombopoyesis"],
    "respuesta_correcta": "B",
    "explicacion": "La warfarina actúa inhibiendo la enzima epóxido reductasa, interfiriendo con la activación de la vitamina K."
  }
]
"""
    else:
        raise ValueError("Tipo de pregunta no reconocido: usa 'clinica' o 'conceptual'")

    return f"""{instrucciones}

Texto base:
\"\"\"{texto_usuario}\"\"\"
"""
