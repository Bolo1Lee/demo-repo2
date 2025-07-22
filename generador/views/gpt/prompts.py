
def generar_prompt(texto_usuario: str, tipo: str = "clinica", cantidad: int = 10) -> str:
    if tipo == "clinica":
        instrucciones = f"""
Eres un generador de preguntas de opción múltiple para estudiantes de medicina. A partir del siguiente texto, genera exactamente {cantidad} preguntas que cumplan los siguientes criterios:

- Dirigidas a estudiantes clínicos avanzados.
- Evalúan aplicación de conocimientos en contextos clínicos.
- Cada pregunta debe tener un breve caso clínico.
- Cada pregunta debe tener exactamente 4 alternativas, como una lista de strings.
- El campo "alternativas" debe ser una lista: ["alternativa A", "alternativa B", "alternativa C", "alternativa D"]
- No incluyas letras como "A." o "B." en las alternativas.
- Solo una alternativa es correcta (indicar con "respuesta_correcta": "B", por ejemplo).
- Incluir una breve justificación en el campo "explicacion".

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
        instrucciones = """
Eres un generador de preguntas de opción múltiple para estudiantes de medicina. A partir del siguiente texto, genera exactamente {cantidad} preguntas que cumplan los siguientes criterios:

- Dirigidas a estudiantes en formación básica.
- Evalúan conceptos fundamentales.
- Cada pregunta debe tener exactamente 4 alternativas en una lista de strings.
- No usar letras ("A." o "B.") en las alternativas.
- Solo una es correcta ("respuesta_correcta": "C", por ejemplo).
- Agrega una justificación en el campo "explicacion".

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
