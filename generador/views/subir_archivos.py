from django.shortcuts import render
from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar la clave de API desde el archivo .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from django.contrib.auth.decorators import login_required

@login_required
def subir_archivo(request):
    respuesta = None
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        contenido = archivo.read().decode("utf-8", errors="replace")  # le agregamos esto para evitar errores

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
