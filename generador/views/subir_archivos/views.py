import os
from django.shortcuts import render
from ...models import Documento, Tema
from generador.views.gpt.helpers import generar_preguntas_y_guardar
from generador.views.subir_archivos.extraccion import extraer_texto_pdf, extraer_texto_ppt
from generador.views.subir_archivos.limpieza import limpiar_texto

from openai import OpenAI
from dotenv import load_dotenv

# Cargar configuración de GPT
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o")
temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 3000))
client = OpenAI(api_key=api_key)

def subir_documento(request):
    preguntas = []
    error = None

    if request.method == "POST":
        archivo = request.FILES.get('archivo')
        tema_existente = request.POST.get("tema_existente")
        tema_nuevo = request.POST.get("tema_nuevo", "").strip()

        tema_asociado = None
        if tema_nuevo:
            tema_asociado, _ = Tema.objects.get_or_create(nombre=tema_nuevo)
        elif tema_existente:
            tema_asociado = Tema.objects.filter(id=tema_existente).first()

        tipo = request.POST.get("tipo", "clinica")
        cantidad = int(request.POST.get("cantidad", 5))


        if not archivo or not tema_asociado:
            error = "Debes seleccionar un archivo y un tema."
        else:
            documento = Documento.objects.create(
                archivo=archivo,
                usuario=request.user,
                tema=tema_asociado
            )

            ruta = documento.archivo.path
            extension = os.path.splitext(ruta)[1].lower()

            # Extraer texto según tipo
            if extension == ".pdf":
                texto = extraer_texto_pdf(ruta)
            elif extension in [".ppt", ".pptx"]:
                texto = extraer_texto_ppt(ruta)
            elif extension == ".txt":
                with open(ruta, 'r', encoding='utf-8') as f:
                    texto = f.read()
            else:
                error = "Formato no soportado."

            if not error:
                texto = limpiar_texto(texto)
                #tema_asociado = Tema.objects.filter(id=tema_id).first()

                try:
                    preguntas, _ = generar_preguntas_y_guardar(
                        texto, tipo, cantidad, tema_asociado,
                        client, model, temperature, max_tokens
                    )
                except Exception as e:
                    error = f"Ocurrió un error al generar preguntas: {str(e)}"

    # Mostrar formulario y preguntas (si hay)
    temas = Tema.objects.all()
    return render(request, "subir_documento.html", {
        "temas": temas,
        "preguntas": preguntas,
        "error": error
    })
