from django.shortcuts import render, get_object_or_404
from .models import Nivel, Desafio # Importamos Desafio también
from .logic import generar_sopa

def home(request):
    # Obtenemos todos los niveles ordenados por su número
    niveles = Nivel.objects.all().order_by('numero')
    return render(request, 'index.html', {'niveles': niveles})

def jugar(request, nivel_id): 
    # Obtenemos el objeto del nivel
    nivel = get_object_or_404(Nivel, id=nivel_id)
    
    # IMPORTANTE: Como quitamos el ForeignKey, buscamos los desafíos 
    # filtrando por el ID del nivel (convertido a string para MongoDB)
    desafios = Desafio.objects.filter(nivel=str(nivel.id))
    
    # Extraemos solo las palabras para el algoritmo de la sopa
    palabras = [d.palabra for d in desafios]
    
    # Generamos la sopa de letras
    # Si no hay desafíos aún, pasamos una lista vacía para que no truene logic.py
    sopa = generar_sopa(palabras, tamaño=nivel.dimension)
    
    return render(request, 'juego.html', {
        'nivel': nivel,
        'sopa': sopa,
        'desafios': desafios
    })
