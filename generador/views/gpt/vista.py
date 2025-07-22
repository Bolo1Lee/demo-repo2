from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from generador.models import Tema
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

from .prompts import generar_prompt
from .helpers import limpiar_preguntas_json, guardar_preguntas

# 🔐 Cargar variables desde .env
load_dotenv()

# Leer configuración segura
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o")
temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 3000))

if not api_key:
    raise ValueError("No se encontró la variable OPENAI_API_KEY en el archivo .env.")

# Inicializar cliente
client = OpenAI(api_key=api_key)

@login_required
def pregunta_chatgpt(request):
    respuesta_raw = None
    preguntas = None
    error_json = None

    temas_disponibles = Tema.objects.all()

    # Inicializar variables por defecto para GET
    tema_existente = ""
    texto = ""
    tipo = "clinica"
    cantidad = 5

    if request.method == "POST":
        texto = request.POST.get("texto_usuario", "")
        tema_existente = request.POST.get("tema_existente")
        tema_nuevo = request.POST.get("tema_nuevo", "").strip()
        tipo = request.POST.get("tipo", "clinica")
        cantidad = int(request.POST.get("cantidad", 5))
        if cantidad > 20:
            cantidad = 20  # límite defensivo

        tema_asociado = None
        if tema_nuevo:
            tema_asociado, _ = Tema.objects.get_or_create(nombre=tema_nuevo)
        elif tema_existente:
            try:
                tema_asociado = Tema.objects.get(id=tema_existente)
            except Tema.DoesNotExist:
                tema_asociado = None

        if texto.strip() and tema_asociado:
            prompt = generar_prompt(texto_usuario=texto, tipo=tipo, cantidad=cantidad)

            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Eres un generador de preguntas tipo prueba clínica universitaria en formato JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                respuesta_raw = completion.choices[0].message.content

                if not respuesta_raw or not respuesta_raw.strip():
                    error_json = "La respuesta de OpenAI está vacía o no contiene datos."
                else:
                    try:
                        preguntas_limpias = limpiar_preguntas_json(respuesta_raw)
                        preguntas_guardadas, _ = guardar_preguntas(preguntas_limpias, tema_asociado)
                        preguntas = preguntas_guardadas[:cantidad]
                    except Exception as e:
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
        "modelo_usado": model,
    })
