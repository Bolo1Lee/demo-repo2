from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from generador.models import Tema
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

from .prompts import generar_prompt
from .helpers import limpiar_preguntas_json, guardar_preguntas, generar_preguntas_y_guardar

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
    preguntas = []
    preguntas_descartadas = []
    respuesta_raw = None
    modelo_usado = None
    error_json = None

    # Cargar solo los temas del usuario
    temas_disponibles = Tema.objects.filter(usuario=request.user)

    # Inicializar valores para GET
    tema_existente = ""
    texto = ""
    tipo = "clinica"
    cantidad = 5

    if request.method == "POST":
        texto = request.POST.get("texto_usuario", "")
        tema_existente = request.POST.get("tema_existente")
        tema_nuevo = request.POST.get("tema_nuevo", "").strip()
        tema_padre_id = request.POST.get("tema_padre")
        tipo = request.POST.get("tipo", "clinica")
        cantidad = int(request.POST.get("cantidad", 5))
        if cantidad > 20:
            cantidad = 20  # límite de seguridad

        # Asociar tema
        tema_asociado = None
        if tema_nuevo:
            tema_padre = Tema.objects.filter(id=tema_padre_id, usuario=request.user).first() if tema_padre_id else None
            tema_asociado, _ = Tema.objects.get_or_create(
                nombre=tema_nuevo,
                usuario=request.user,
                padre=tema_padre
            )
        elif tema_existente:
            tema_asociado = Tema.objects.filter(id=tema_existente, usuario=request.user).first()

        if texto.strip() and tema_asociado:
            try:
                preguntas, preguntas_descartadas, respuesta_raw = generar_preguntas_y_guardar(
                    texto, tipo, cantidad, tema_asociado,
                    client, model, temperature, max_tokens, request.user
                )
            except Exception as e:
                error_json = f"Ocurrió un error: {str(e)}"

    return render(request, "formulario.html", {
        "respuesta_raw": respuesta_raw,
        "preguntas": preguntas,
        "preguntas_descartadas": preguntas_descartadas,
        "error_json": error_json,
        "temas": temas_disponibles,
        "tema_seleccionado_id": tema_existente or "",
        "texto_usuario": texto,
        "tipo_seleccionado": tipo,
        "cantidad_seleccionada": cantidad,
        "modelo_usado": model,
    })


@login_required
def pregunta_desde_documento(request):
    respuesta_raw = None
    preguntas = []
    error_json = None

    texto = request.session.pop("texto_procesado", None)
    tema_id = request.session.get("tema_procesado")

    tipo = "clinica"
    cantidad = 5

    # Temas visibles para el usuario
    temas_disponibles = Tema.objects.filter(usuario=request.user)

    tema_asociado = Tema.objects.filter(id=tema_id, usuario=request.user).first() if tema_id else None

    if not texto or not tema_asociado:
        return render(request, "formulario.html", {
            "error_json": "No se encontró texto o tema válido. Sube un documento primero.",
            "temas": temas_disponibles,
            "tema_seleccionado_id": "",
            "texto_usuario": "",
            "tipo_seleccionado": tipo,
            "cantidad_seleccionada": cantidad,
            "modelo_usado": model
        })

    try:
        preguntas, preguntas_descartadas, respuesta_raw = generar_preguntas_y_guardar(
            texto, tipo, cantidad, tema_asociado,
            client, model, temperature, max_tokens,
            request.user
        )
    except Exception as e:
        error_json = f"Ocurrió un error al generar preguntas: {str(e)}"

    return render(request, "formulario.html", {
        "respuesta_raw": respuesta_raw,
        "preguntas": preguntas,
        "preguntas_descartadas": preguntas_descartadas,
        "error_json": error_json,
        "temas": temas_disponibles,
        "tema_seleccionado_id": tema_id or "",
        "texto_usuario": texto,
        "tipo_seleccionado": tipo,
        "cantidad_seleccionada": cantidad,
        "modelo_usado": model,
    })
