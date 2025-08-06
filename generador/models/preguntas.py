from django.db import models
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
        unique_together = ('nombre', 'usuario', 'padre')

    def __str__(self):
        return f"{self.padre} > {self.nombre}" if self.padre else self.nombre


class Pregunta(models.Model):
    pregunta = models.TextField()
    alternativa_a = models.CharField(max_length=300)
    alternativa_b = models.CharField(max_length=300)
    alternativa_c = models.CharField(max_length=300)
    alternativa_d = models.CharField(max_length=300)
    respuesta_correcta = models.CharField(max_length=1)
    explicacion = models.TextField()
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.pregunta[:80] + "..."
