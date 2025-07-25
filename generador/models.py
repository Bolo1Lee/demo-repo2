from django.db import models
from django.utils import timezone
from datetime import timedelta

class Tema(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Pregunta(models.Model):
    pregunta = models.TextField()
    alternativa_a = models.CharField(max_length=300)
    alternativa_b = models.CharField(max_length=300)
    alternativa_c = models.CharField(max_length=300)
    alternativa_d = models.CharField(max_length=300)
    respuesta_correcta = models.CharField(max_length=1)  # Solo A, B, C o D
    explicacion = models.TextField()
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.pregunta[:80] + "..."



class Repeticion(models.Model):
    RESPUESTA_CHOICES = [
        (0, 'Incorrecta'),
        (1, 'Difícil'),
        (2, 'Bien'),
        (3, 'Fácil'),
    ]

    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    fecha_revisada = models.DateTimeField(auto_now=True)
    proxima_repeticion = models.DateTimeField(default=timezone.now)
    nivel_respuesta = models.IntegerField(choices=RESPUESTA_CHOICES, default=0)
    fecha_ultima_respuesta = models.DateTimeField(null=True, blank=True)


    def actualizar_repeticion(self, nivel):
        ahora = timezone.now()
        if nivel == 0:
            self.proxima_repeticion = ahora + timedelta(minutes=1)
        elif nivel == 1:
            self.proxima_repeticion = ahora + timedelta(minutes=5)
        elif nivel == 2:
            self.proxima_repeticion = ahora + timedelta(minutes=10)
        elif nivel == 3:
            self.proxima_repeticion = ahora + timedelta(days=1)
        self.nivel_respuesta = nivel
        self.save()

    def __str__(self):
        return f"{self.pregunta} - Repetir en: {self.proxima_repeticion.strftime('%Y-%m-%d %H:%M')}"

from django.contrib.auth.models import User  # Asegúrate de tener esto al inicio si no lo tienes

class Documento(models.Model):
    archivo = models.FileField(upload_to='documentos/')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.archivo.name
