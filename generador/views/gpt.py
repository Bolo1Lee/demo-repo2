from django.shortcuts import render
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from generador.models import Pregunta, Tema

# Cargar la clave de API desde el archivo .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from django.contrib.auth.decorators import login_required

@login_required
def pregunta_chatgpt(request):
    respuesta_raw = None     # Texto plano que devuelve GPT
    preguntas = None         # Lista de preguntas ya convertida (si JSON es válido)
    error_json = None        # Mensaje si el JSON está mal

    # Obtener todos los temas para el dropdown
    temas_disponibles = Tema.objects.all()

    if request.method == "POST":
        texto = request.POST.get("texto_usuario", "")
        tema_existente = request.POST.get("tema_existente")
        tema_nuevo = request.POST.get("tema_nuevo", "").strip()

        # Validar o crear el tema seleccionado
        tema_asociado = None
        if tema_nuevo:
            tema_asociado, _ = Tema.objects.get_or_create(nombre=tema_nuevo)
        elif tema_existente:
            try:
                tema_asociado = Tema.objects.get(id=tema_existente)
            except Tema.DoesNotExist:
                tema_asociado = None  # fallback

        if texto.strip() and tema_asociado:
            prompt = f"""
Eres un generador de preguntas de opción múltiple para estudiantes de medicina. A partir del siguiente texto, genera preguntas que cumplan los siguientes criterios:

- Están dirigidas a estudiantes clínicos avanzados.
- Evalúan aplicación de conocimientos en contextos clínicos (no memorización).
- Cada pregunta debe tener un breve caso clínico o situación médica concreta.
- Solo una alternativa es correcta.
- Las otras alternativas deben ser plausibles, pero incorrectas.
- Debe incluir una breve justificación explicando por qué la respuesta correcta lo es.

FORMATO ESTRICTO (JSON):

[
  {{
    "pregunta": "Mujer de 65 años con DM2 consulta por dolor torácico súbito. ¿Cuál es el siguiente paso más adecuado?",
    "alternativas": ["A. ECG de control", "B. Medir troponinas", "C. Administrar AINEs", "D. Observación ambulatoria"],
    "respuesta_correcta": "B",
    "explicacion": "El dolor torácico súbito en paciente con riesgo cardiovascular debe ser evaluado inicialmente con marcadores de daño miocárdico como troponinas."
  }},
  ...
]

Texto base:
\"\"\"{texto}\"\"\"
"""

            try:
                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un generador de preguntas tipo prueba clínica universitaria en formato JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                respuesta_raw = completion.choices[0].message.content

                # VALIDAR JSON
                try:
                    preguntas = json.loads(respuesta_raw)

                    for item in preguntas:
                        alternativas = item.get("alternativas", [])
                        if len(alternativas) >= 4:
                            nueva = Pregunta(
                                pregunta=item["pregunta"],
                                alternativa_a=alternativas[0],
                                alternativa_b=alternativas[1],
                                alternativa_c=alternativas[2],
                                alternativa_d=alternativas[3],
                                respuesta_correcta=item["respuesta_correcta"],
                                explicacion=item["explicacion"],
                                tema=tema_asociado
                            )
                            nueva.save()

                except json.JSONDecodeError as e:
                    error_json = f"El JSON generado es inválido: {str(e)}"

            except Exception as e:
                respuesta_raw = f"Error al generar preguntas: {str(e)}"

    return render(request, "formulario.html", {
        "respuesta_raw": respuesta_raw,
        "preguntas": preguntas,
        "error_json": error_json,
        "temas": temas_disponibles
    })
