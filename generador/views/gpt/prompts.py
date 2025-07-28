def generar_prompt(texto_usuario: str, tipo: str = "clinica", cantidad: int = 10) -> str:
    if tipo == "clinica":
        instrucciones = f"""
Eres un generador de preguntas de opción múltiple para estudiantes de medicina. A partir del siguiente texto, genera exactamente {cantidad} preguntas que cumplan los siguientes criterios:

- Dirigidas a estudiantes clínicos avanzados.
- Evalúan aplicación de conocimientos en contextos clínicos.
- Cada pregunta debe iniciar con un caso clínico completo que incluya: edad, sexo, síntomas principales, antecedentes relevantes, hallazgos físicos y exámenes complementarios cuando sea necesario. Debe entregar la información suficiente para razonar clínicamente.
- Cuando sea relevante, incluye resultados de laboratorio, exámenes de imágenes descritas en texto, o hallazgos complementarios que ayuden al razonamiento clínico.
- Las 4 alternativas deben ser plausibles y pertenecer a la misma categoría diagnóstica o terapéutica, evitando distractores irrelevantes.
- Cada pregunta debe tener exactamente 4 alternativas, como una lista de strings.
- El campo "alternativas" debe ser una lista: ["alternativa A", "alternativa B", "alternativa C", "alternativa D"]
- No incluyas letras como "A." o "B." en las alternativas.
- Solo una alternativa es correcta.
- El campo "respuesta_correcta" debe contener exclusivamente una letra mayúscula entre "A", "B", "C" o "D" que represente la posición de la alternativa correcta. No pongas el texto de la alternativa como respuesta.
- Incluir una breve justificación en el campo "explicacion".
- Evita preguntas triviales o que se resuelvan con definiciones simples. Prioriza aquellas que requieren análisis o integración de información.
- No repitas enunciados o explicaciones entre preguntas.

FORMATO ESTRICTO (JSON):
[
  {{
    "pregunta": "Paciente de 60 años con disnea y edema bilateral. ¿Cuál es la causa más probable?",
    "alternativas": ["Insuficiencia hepática", "Insuficiencia cardíaca", "Síndrome nefrótico", "Tromboembolismo pulmonar"],
    "respuesta_correcta": "B",
    "explicacion": "La disnea con edema bilateral es clásica de insuficiencia cardíaca congestiva."
  }}
] # Total: {cantidad} elementos
"""
    elif tipo == "conceptual":
        instrucciones = f"""
Eres un generador de preguntas de opción múltiple para estudiantes de medicina. A partir del siguiente texto, genera exactamente {cantidad} preguntas que cumplan los siguientes criterios:

- Dirigidas a estudiantes en formación básica.
- Evalúan conceptos fundamentales.
- Cada pregunta debe tener exactamente 4 alternativas en una lista de strings.
- No usar letras ("A." o "B.") en las alternativas.
- Solo una es correcta.
- El campo "respuesta_correcta" debe contener exclusivamente una letra mayúscula entre "A", "B", "C" o "D" que represente la posición de la alternativa correcta. No pongas el texto de la alternativa como respuesta.
- Agrega una justificación en el campo "explicacion".
- Las 4 alternativas deben estar relacionadas temáticamente y evitar distractores absurdos.
- No repitas enunciados o explicaciones entre preguntas.

FORMATO ESTRICTO (JSON):
[
  {{
    "pregunta": "¿Cuál es el principal sitio de reabsorción de sodio en el nefrón?",
    "alternativas": ["Túbulo distal", "Asa de Henle", "Túbulo proximal", "Conducto colector"],
    "respuesta_correcta": "C",
    "explicacion": "El túbulo proximal reabsorbe aproximadamente el 65% del sodio filtrado."
  }}
] # Total: {cantidad} elementos
"""
    else:
        raise ValueError("Tipo de pregunta no reconocido: usa 'clinica' o 'conceptual'")

    return f"""{instrucciones}

Texto base:
\"\"\"{texto_usuario}\"\"\"
"""
