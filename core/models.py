# ARCHIVO: core/models.py
from django.db import models

class Nivel(models.Model):
    # Declaramos campos virtuales para que el Admin sepa qué pintar
    numero = models.IntegerField(primary_key=True)
    titulo = models.CharField(max_length=200)
    dimension = models.IntegerField(default=10)
    desbloqueado = models.BooleanField(default=True)

    class Meta:
        managed = False  # CRÍTICO: Evita que Django busque una tabla SQLite
        verbose_name_plural = "Niveles (MongoDB)"

class Subtema(models.Model):
    id_subtema = models.AutoField(primary_key=True)
    nombre_subtema = models.CharField(max_length=200)

    class Meta:
        managed = False
        verbose_name_plural = "Subtemas (MongoDB)"

class NivelProgresion(models.Model):
    id_nivel_prog = models.AutoField(primary_key=True)
    id_nivel = models.IntegerField()
    id_subtema = models.IntegerField()

    class Meta:
        managed = False
        verbose_name_plural = "Progresiones (MongoDB)"

class PalabraDesafio(models.Model):
    palabra = models.CharField(max_length=100, primary_key=True)
    pista = models.TextField()
    id_subtema = models.IntegerField()

    class Meta:
        managed = False
        verbose_name_plural = "Palabras Desafío (MongoDB)"
