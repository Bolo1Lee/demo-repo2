from django.shortcuts import render
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from .models import Pregunta, Tema

# Cargar la clave de API desde el archivo .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
\"\"\"
{texto}
\"\"\"
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


def subir_archivo(request):
    respuesta = None
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        contenido = archivo.read().decode("utf-8")

        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un asistente útil que resume textos."},
                    {"role": "user", "content": contenido}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            respuesta = completion.choices[0].message.content

        except Exception as e:
            respuesta = f"Error al resumir texto: {str(e)}"

    return render(request, "subir_archivo.html", {"respuesta": respuesta})


from django.shortcuts import render, redirect
from .models import Pregunta, Tema
import random

def practicar(request):
    temas = Tema.objects.all()
    tema_seleccionado = request.GET.get("tema", "")
    pregunta = None
    mensaje = ""
    mostrar_explicacion = False

    if tema_seleccionado:
        preguntas_tema = Pregunta.objects.filter(tema__nombre=tema_seleccionado)
        if preguntas_tema.exists():
            pregunta = random.choice(list(preguntas_tema))

    if request.method == "POST":
        pregunta_id = int(request.POST.get("pregunta_id"))
        respuesta_usuario = request.POST.get("respuesta")
        pregunta = Pregunta.objects.get(id=pregunta_id)
        mostrar_explicacion = True

        if respuesta_usuario == pregunta.respuesta_correcta:
            mensaje = "✅ ¡Correcto!"
        else:
            mensaje = f"❌ Incorrecto. La respuesta correcta era: {pregunta.respuesta_correcta}"

    return render(request, "practicar.html", {
        "temas": temas,
        "pregunta": pregunta,
        "mensaje": mensaje,
        "mostrar_explicacion": mostrar_explicacion,
        "tema_seleccionado": tema_seleccionado,
    })


def lista_preguntas(request):
    tema = request.GET.get("tema", "")
    q = request.GET.get("q", "")

    preguntas = Pregunta.objects.all().select_related('tema')

    if tema:
        preguntas = preguntas.filter(tema__nombre=tema)
    if q:
        preguntas = preguntas.filter(pregunta__icontains=q)

    temas = Tema.objects.all()

    return render(request, "lista_preguntas.html", {
        "preguntas": preguntas,
        "temas": temas,
        "tema_seleccionado": tema,
        "busqueda_actual": q
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import Pregunta, Tema

from django.shortcuts import render, redirect, get_object_or_404
from .models import Pregunta, Tema

def editar_pregunta(request, pregunta_id):
    pregunta = get_object_or_404(Pregunta, id=pregunta_id)
    temas = Tema.objects.all()
    errores = []

    if request.method == "POST":
        # Obtener los datos del formulario
        pregunta_texto = request.POST.get("pregunta", "")
        alternativa_a = request.POST.get("alternativa_a", "")
        alternativa_b = request.POST.get("alternativa_b", "")
        alternativa_c = request.POST.get("alternativa_c", "")
        alternativa_d = request.POST.get("alternativa_d", "")
        respuesta_correcta = request.POST.get("respuesta_correcta", "")
        explicacion = request.POST.get("explicacion", "")
        tema_id = request.POST.get("tema")

        # Validaciones
        if not pregunta_texto.strip():
            errores.append("La pregunta no puede estar vacía.")
        if respuesta_correcta not in ["A", "B", "C", "D"]:
            errores.append("La respuesta correcta debe ser A, B, C o D.")
        if not alternativa_a or not alternativa_b or not alternativa_c or not alternativa_d:
            errores.append("Todas las alternativas deben estar completas.")
        if not explicacion.strip():
            errores.append("La explicación no puede estar vacía.")
        if not tema_id:
            errores.append("Debes seleccionar un tema.")

        # Si no hay errores, guardar
        if not errores:
            pregunta.pregunta = pregunta_texto
            pregunta.alternativa_a = alternativa_a
            pregunta.alternativa_b = alternativa_b
            pregunta.alternativa_c = alternativa_c
            pregunta.alternativa_d = alternativa_d
            pregunta.respuesta_correcta = respuesta_correcta
            pregunta.explicacion = explicacion
            pregunta.tema = Tema.objects.get(id=tema_id)
            pregunta.save()
            return redirect("lista_preguntas")

    return render(request, "editar_pregunta.html", {
        "pregunta": pregunta,
        "temas": temas,
        "errores": errores
    })
