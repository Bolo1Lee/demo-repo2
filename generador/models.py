from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class Tema(models.Model):
    nombre = models.CharField(max_length=100)
    padre = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subtemas',
        on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nombre', 'usuario', 'padre')  # Evita duplicados por usuario

    def __str__(self):
        if self.padre:
            return f"{self.padre} > {self.nombre}"
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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

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

    # FSRS nuevos campos
    stability = models.FloatField(default=1.0)
    difficulty = models.FloatField(default=0.3)
    interval = models.FloatField(default=0.0)  # en días
    lapses = models.IntegerField(default=0)

    def actualizar_repeticion(self, nivel):
        import math
        ahora = timezone.now()

        alpha = 0.4
        beta = 0.3
        gamma = 0.05
        delta = 0.05
        theta = 1
        target_retrievability = 0.9

        if self.fecha_ultima_respuesta:
            t = (ahora - self.fecha_ultima_respuesta).days
            t = max(t, 0.01)
        else:
            t = 0.01
        r = math.exp(-theta * t / self.stability)

        if nivel == 0:
            self.stability *= (1 - beta * r * self.difficulty)
            self.difficulty = min(1.0, self.difficulty + delta * r)
            self.lapses += 1
        else:
            self.stability *= (1 + alpha * (1 - r) * (1 - self.difficulty))
            self.difficulty = max(0.0, self.difficulty - gamma * (1 - r))

        self.interval = self.stability * math.log(1 / (1 - target_retrievability))
        self.proxima_repeticion = ahora + timedelta(days=self.interval)

        self.nivel_respuesta = nivel
        self.save()

    def __str__(self):
        return f"{self.pregunta} - Repetir en: {self.proxima_repeticion.strftime('%Y-%m-%d %H:%M')}"

class Documento(models.Model):
    archivo = models.FileField(upload_to='documentos/')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.archivo.name
