from django.shortcuts import render
from generador.models import Tema
from generador.views.subir_archivos.extraccion import (
    extraer_texto_pdf,
    extraer_texto_ppt
)
from generador.views.gpt.helpers import generar_preguntas_y_guardar
from generador.views.subir_archivos.limpieza import limpiar_texto

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o")
temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 3000))
client = OpenAI(api_key=api_key)

def subir_documento(request):
    temas = Tema.objects.filter(usuario=request.user)
    preguntas = []
    preguntas_descartadas = []
    respuesta_raw = None
    error = None

    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        tipo = request.POST.get("tipo", "clinica")
        cantidad = int(request.POST.get("cantidad", 5))

        tema_existente = request.POST.get("tema_existente")
        tema_nuevo = request.POST.get("tema_nuevo", "").strip()
        tema_padre_id = request.POST.get("tema_padre")

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

        if not archivo or not tema_asociado:
            error = "Debe subir un archivo y seleccionar o crear un tema."

        texto = ""
        if archivo.name.endswith(".pdf"):
            texto = extraer_texto_pdf(archivo)
        elif archivo.name.endswith((".ppt", ".pptx")):
            texto = extraer_texto_ppt(archivo)
        elif archivo.name.endswith(".txt"):
            texto = archivo.read().decode("utf-8")
        else:
            error = "Formato de archivo no soportado."

        if not texto:
            error = "No se pudo extraer texto del archivo."

        if not error:
            texto = limpiar_texto(texto)

            try:
                preguntas, preguntas_descartadas, respuesta_raw = generar_preguntas_y_guardar(
                    texto, tipo, cantidad, tema_asociado,
                    client, model, temperature, max_tokens,
                    request.user
                )
            except Exception as e:
                error = f"Ocurrió un error al generar preguntas: {str(e)}"

    return render(request, "subir_documento.html", {
        "temas": temas,
        "preguntas": preguntas,
        "preguntas_descartadas": preguntas_descartadas,
        "respuesta_raw": respuesta_raw,
        "error": error
    })
