from django.urls import path
from .views.home import home
from .views.gpt import pregunta_chatgpt
from .views.subir_archivos import subir_archivo
from .views.practica import practicar
from .views.preguntas import lista_preguntas, editar_pregunta
from .views.usuarios import registro, login_view, logout_view
from generador.views.anki.vista import anki_view



urlpatterns = [
    path("", home, name="home"),  # Página principal
    path("subir/", subir_archivo, name="subir_archivo"),  # Subir txt o PDF (futuro)
    path("pregunta/", pregunta_chatgpt, name="pregunta_chatgpt"),  # Generar preguntas con texto base
    path("preguntas/", lista_preguntas, name="lista_preguntas"),  # Ver todas las preguntas
    path("preguntas/editar/<int:pregunta_id>/", editar_pregunta, name="editar_pregunta"),  # Editar pregunta
    path("registro/", registro, name="registro"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('practicar/', anki_view, name='practicar'),

]

