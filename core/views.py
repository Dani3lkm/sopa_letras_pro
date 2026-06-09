import logging
from django.shortcuts import render
from django.http import Http404
from pymongo import MongoClient
from .logic import generar_sopa
import os
from pymongo import MongoClient

MONGO_URI = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')

try:
    # Conectamos usando la variable dinámica
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client['chemical_core_nosql']
    client.admin.command('ping')
    print("▶ [ESTADO: OK] Conexión establecida con MongoDB.")
except Exception as e:
    print(f"❌ [CRÍTICO] Fallo en la capa de datos NoSQL: {e}")
    db = None

logger = logging.getLogger(__name__)

try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    db = client['chemical_core_nosql']
    client.admin.command('ping')
    print("▶ [ESTADO: OK] Conexión síncrona establecida con MongoDB en Podman.")
except Exception as e:
    print(f"❌ [CRÍTICO] Fallo en la capa de datos NoSQL: {e}")
    db = None


def home(request):
    if db is None:
        return render(request, 'error_db.html', {'error': 'Capa de persistencia NoSQL no disponible.'})
    
    print("\n[PETICIÓN: GET] Solicitando índice de niveles desde colección 'niveles'...")
    
    try:
        niveles_cursor = db.niveles.find().sort("numero", 1)
        
        niveles = []
        for doc in niveles_cursor:
            # Usamos un valor por defecto si 'numero' no viene en el documento de Mongo
            num = doc.get('numero', 1)
            
            niveles.append({
                'id_nivel': str(num),
                'numero': num,
                'titulo': doc.get('titulo', 'Nivel sin título').upper()
            })
            
        print(f"▶ [MONGO] Se cargaron {len(niveles)} niveles exitosamente para el menú.")
        return render(request, 'index.html', {'niveles': niveles})
        
    except Exception as e:
        logger.error(f"Error al iterar documentos en home: {e}")
        raise Http404("Error interno al procesar los documentos de niveles.")

def jugar(request, nivel_id):
    if db is None:
        raise Http404("El servicio de persistencia documental no está activo.")

    print(f"\n[PETICIÓN: GET] Inicializando protocolo de juego para Nivel Número: {nivel_id}")

    nivel_doc = db.niveles.find_one({"numero": int(nivel_id)})
    
    if not nivel_doc:
        print(f"❌ [ERROR 404] Identificador {nivel_id} no mapeado en MongoDB.")
        raise Http404("El protocolo de nivel solicitado no existe.")
    
    desafios_compatibles = []
    palabras = []
    
    subtemas_lista = nivel_doc.get('subtemas', [])
    for subtema in subtemas_lista:
        palabras_desafio = subtema.get('palabras_desafio', [])
        for item in palabras_desafio:
            raw_palabra = item.get('palabra', '')
            pista_text = item.get('pista', '')
            
            if raw_palabra and pista_text:
                palabra_limpia = raw_palabra.upper().strip()
                palabras.append(palabra_limpia)
                
                desafios_compatibles.append({
                    'palabra': palabra_limpia,
                    'pista': pista_text,
                    'nombre': palabra_limpia
                })

    if not palabras:
        palabras = ["MONGO", "NOSQL", "PODMAN"]
        desafios_compatibles = [
            {'palabra': "MONGO", 'pista': "Base de datos documental.", 'nombre': "MONGO"},
            {'palabra': "NOSQL", 'pista': "Paradigma sin esquemas rígidos.", 'nombre': "NOSQL"},
            {'palabra': "PODMAN", 'pista': "Contenedor aislado.", 'nombre': "PODMAN"}
        ]

    dimension_tablero = nivel_doc.get('dimension', 10)
    sopa_generada = generar_sopa(palabras, tamaño=dimension_tablero)

    nivel_contexto = {
        'id_nivel': str(nivel_doc['_id']),
        'numero': nivel_doc.get('numero'),
        'titulo': nivel_doc.get('titulo', 'Nivel Indefinido'),
        'dimension': dimension_tablero
    }
    
    return render(request, 'juego.html', {
        'nivel': nivel_contexto,
        'sopa': sopa_generada,
        'desafios': desafios_compatibles
    })

def admin_nosql(request):
    if db is None:
        return render(request, 'error_db.html', {'error': 'MongoDB fuera de servicio.'})

    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'guardar':
            # Extraemos las listas dinámicas enviadas por el formulario de Tailwind
            lista_palabras = request.POST.getlist('palabras[]')
            lista_pistas = request.POST.getlist('pistas[]')
            
            # Formateamos los subdocumentos embebidos puros de MongoDB
            palabras_desafio = []
            for p, pista in zip(lista_palabras, lista_pistas):
                if p.strip() and pista.strip():
                    palabras_desafio.append({
                        "palabra": p.upper().strip(),
                        "pista": pista.strip()
                    })

            nuevo_nivel = {
                "numero": int(request.POST.get('numero')),
                "titulo": request.POST.get('titulo').upper().strip(),
                "dimension": int(request.POST.get('dimension', 12)),
                "subtemas": [
                    {
                        "nombre_subtema": request.POST.get('subtema').strip(),
                        "palabras_desafio": palabras_desafio
                    }
                ]
            }
            
            # Insertamos el documento jerárquico puro en Podman
            db.niveles.insert_one(nuevo_nivel)
            print(f"▶ [ADMIN NOSQL] Nivel {request.POST.get('numero')} guardado con {len(palabras_desafio)} palabras embebidas.")
            
        elif accion == 'eliminar':
            num_eliminar = int(request.POST.get('numero_eliminar'))
            db.niveles.delete_one({"numero": num_eliminar})
            print(f"▶ [ADMIN NOSQL] Documento de nivel {num_eliminar} eliminado.")

    niveles_cursor = db.niveles.find().sort("numero", 1)
    niveles = list(niveles_cursor)

    return render(request, 'admin_nosql.html', {'niveles': niveles})
