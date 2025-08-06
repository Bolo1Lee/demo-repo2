from django.db import models
from django.utils import timezone
from datetime import timedelta
from .preguntas import Pregunta

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
    modo = models.CharField(max_length=20, default="normal")


    # Estos campos se pueden seguir usando en el futuro si vuelves al algoritmo FSRS
    stability = models.FloatField(default=1.0)
    difficulty = models.FloatField(default=0.3)
    interval = models.FloatField(default=0.0)
    lapses = models.IntegerField(default=0)

    def actualizar_repeticion(self, nivel):
        ahora = timezone.now()

        # 🔁 Repetición compacta adaptada a estudio con pruebas semanales
        if nivel == 0:  # ❌ Incorrecta → repetir en 12 horas
            self.interval = 0.5
            self.lapses += 1
        elif nivel == 1:  # 🟡 Difícil → repetir mañana
            self.interval = 1.0
        elif nivel == 2:  # 🔵 Bien → repetir en 2 días
            self.interval = 2.0
        elif nivel == 3:  # ✅ Fácil → repetir en 3 días
            self.interval = 3.0

        self.proxima_repeticion = ahora + timedelta(days=self.interval)
        self.nivel_respuesta = nivel
        self.fecha_ultima_respuesta = ahora
        self.save()

    def __str__(self):
        return f"{self.pregunta} - Repetir en: {self.proxima_repeticion.strftime('%Y-%m-%d %H:%M')}"

