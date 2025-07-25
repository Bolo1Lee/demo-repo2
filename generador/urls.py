from django.urls import path
from .views.home import home
from .views.gpt.vista import pregunta_chatgpt
from .views.practica import practicar
from .views.preguntas import lista_preguntas, editar_pregunta
from generador.views.preguntas import eliminar_pregunta
from .views.usuarios import registro, login_view, logout_view
from generador.views.anki.vista import anki_view
from generador.views.subir_archivos.views import subir_documento
from generador.views.gpt.vista import pregunta_desde_documento


from django.shortcuts import render


urlpatterns = [
    path("", home, name="home"),  # Página principal
    path("pregunta/", pregunta_chatgpt, name="pregunta_chatgpt"),  # Generar preguntas con texto base
    path("preguntas/", lista_preguntas, name="lista_preguntas"),  # Ver todas las preguntas
    path("preguntas/editar/<int:pregunta_id>/", editar_pregunta, name="editar_pregunta"),  # Editar pregunta
    path("preguntas/eliminar/<int:pregunta_id>/", eliminar_pregunta, name="eliminar_pregunta"),
    path("registro/", registro, name="registro"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('practicar/', anki_view, name='practicar'),
    path ("subir/", subir_documento, name="subir_documento"),
    path("pregunta-desde-doc/", pregunta_desde_documento, name="pregunta_desde_documento"),
   
    path("testmodo/", lambda r: render(r, "test_modo_noche.html")),


]

