from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from generador.models import Tema
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

from .prompts import generar_prompt
from .helpers import limpiar_preguntas_json, guardar_preguntas

# Cargar clave API
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@login_required
def pregunta_chatgpt(request):
    respuesta_raw = None
    preguntas = None
    error_json = None

    temas_disponibles = Tema.objects.all()

    if request.method == "POST":
        texto = request.POST.get("texto_usuario", "")
        tema_existente = request.POST.get("tema_existente")
        tema_nuevo = request.POST.get("tema_nuevo", "").strip()
        tipo = request.POST.get("tipo", "clinica")  # tipo de pregunta: 'clinica' o 'conceptual'

        cantidad = int(request.POST.get("cantidad", 5))
        if cantidad > 20: cantidad = 20  # límite defensivo

        tema_asociado = None
        if tema_nuevo:
            tema_asociado, _ = Tema.objects.get_or_create(nombre=tema_nuevo)
        elif tema_existente:
            try:
                tema_asociado = Tema.objects.get(id=tema_existente)
            except Tema.DoesNotExist:
                tema_asociado = None

        if texto.strip() and tema_asociado:
            prompt = generar_prompt(texto_usuario=texto, tipo=tipo)

            try:
                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un generador de preguntas tipo prueba clínica universitaria en formato JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )
                respuesta_raw = completion.choices[0].message.content

                try:
                    preguntas_generadas = json.loads(respuesta_raw)
                    preguntas_limpias = limpiar_preguntas_json(preguntas_generadas)
                    preguntas_guardadas = guardar_preguntas(preguntas_limpias, tema_asociado)
                    preguntas = preguntas_guardadas[:cantidad]

                except json.JSONDecodeError as e:
                    error_json = f"El JSON generado es inválido: {str(e)}"

            except Exception as e:
                respuesta_raw = f"Error al generar preguntas: {str(e)}"

    return render(request, "formulario.html", {
        "respuesta_raw": respuesta_raw,
        "preguntas": preguntas,
        "error_json": error_json,
        "temas": temas_disponibles,
        "tema_seleccionado_id": tema_existente or "",
        "texto_usuario": texto,
        "tipo_seleccionado": tipo,
        "cantidad_seleccionada": cantidad,
    })
