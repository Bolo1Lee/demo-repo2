from django.db import models
from django.contrib.auth.models import User
from .preguntas import Tema

class Documento(models.Model):
    archivo = models.FileField(upload_to='documentos/')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.archivo.name
