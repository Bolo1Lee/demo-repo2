from django.urls import path
from django.shortcuts import render

# Vistas
from .views.home import home
from .views.gpt.vista import pregunta_chatgpt, pregunta_desde_documento
from .views.usuarios import registro, login_view, logout_view
from .views.anki.vista import anki_view
from .views.subir_archivos.views import subir_documento
from .views.preguntas import (
    lista_preguntas,
    editar_pregunta,
    eliminar_pregunta,
    eliminar_preguntas_multiples,
)
from .views.intensivo.vista import intensivo_view  # 👈 NUEVO

urlpatterns = [
    # Página principal
    path("", home, name="home"),

    # Generación de preguntas (GPT)
    path("pregunta/", pregunta_chatgpt, name="pregunta_chatgpt"),  # nombre clásico
    path("pregunta-desde-doc/", pregunta_desde_documento, name="pregunta_desde_documento"),

    # CRUD de preguntas
    path("preguntas/", lista_preguntas, name="lista_preguntas"),
    path("preguntas/editar/<int:pregunta_id>/", editar_pregunta, name="editar_pregunta"),
    path("preguntas/eliminar/<int:pregunta_id>/", eliminar_pregunta, name="eliminar_pregunta"),
    path("preguntas/eliminar-multiples/", eliminar_preguntas_multiples, name="eliminar_preguntas_multiples"),

    # Subir documentos
    path("subir/", subir_documento, name="subir_documento"),

    # Usuarios
    path("registro/", registro, name="registro"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Práctica tipo Anki
    path("practicar/", anki_view, name="practicar"),

    # Estudio intensivo (ultra repetición)
    path("intensivo/", intensivo_view, name="intensivo"),  # 👈 NUEVO

    # Modo noche (test)
    path("testmodo/", lambda r: render(r, "test_modo_noche.html")),
]
