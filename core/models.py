from django.db import models

class Nivel(models.Model):
    numero = models.IntegerField(unique=True)
    titulo = models.CharField(max_length=100)
    dimension = models.IntegerField(default=15) 
    desbloqueado = models.BooleanField(default=False)

    class Meta:
        ordering = ['numero']

    def __str__(self):
        return f"Nivel {self.numero}: {self.titulo}"

class Desafio(models.Model):
    # Cambiamos a CharField para guardar el ID del nivel sin que Djongo explote
    nivel = models.CharField(max_length=100, verbose_name="ID o Número del Nivel")
    pregunta = models.TextField()
    palabra = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.palabra} (Nivel {self.nivel})"
