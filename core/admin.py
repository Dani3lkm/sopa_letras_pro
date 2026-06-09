from django.contrib import admin
from pymongo import MongoClient
from .models import Nivel, Subtema, NivelProgresion, PalabraDesafio

# CONEXIÓN LOCAL HACIA PODMAN
client = MongoClient('mongodb://localhost:27017/')
db = client['chemical_core_nosql']

@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ('numero', 'titulo', 'dimension', 'desbloqueado')
    ordering = ('numero',)

    def get_queryset(self, request):
        """Sobreescribe la lista del admin leyendo directo de MongoDB"""
        # Limpiamos el queryset virtual de Django
        qs = super().get_queryset(request).none()
        
        # Jalamos los documentos de Mongo y los transformamos en instancias de modelo en memoria
        for doc in db.niveles.find().sort("numero", 1):
            obj = Nivel(
                numero=doc.get('numero'),
                titulo=doc.get('titulo', ''),
                dimension=doc.get('dimension', 10),
                desbloqueado=True
            )
            qs |= Nivel.objects.filter(pk=obj.pk)  # Vinculamos al listado visual
        return qs

    def save_model(self, request, obj, form, change):
        """Guarda o actualiza un documento en MongoDB desde el panel de Django"""
        if change:
            # Si se está editando, actualiza el documento existente
            db.niveles.update_one(
                {"numero": int(obj.numero)},
                {"$set": {"titulo": obj.titulo, "dimension": int(obj.dimension)}}
            )
        else:
            # Si es nuevo, inserta el documento estructurado con el array de subtemas vacío
            db.niveles.insert_one({
                "numero": int(obj.numero),
                "titulo": obj.titulo,
                "dimension": int(obj.dimension),
                "subtemas": []
            })

    def delete_model(self, request, obj):
        """Elimina el documento de MongoDB"""
        db.niveles.delete_one({"numero": int(obj.numero)})


@admin.register(Subtema)
class SubtemaAdmin(admin.ModelAdmin):
    list_display = ('id_subtema', 'nombre_subtema')

    def save_model(self, request, obj, form, change):
        """Inserta subtemas embebidos dentro del documento del Nivel 1 por defecto"""
        # Como es NoSQL, metemos el subtema dentro del array embebido de un nivel
        db.niveles.update_one(
            {"numero": 1},  # Suponiendo que los gestionas sobre el nivel 1 de prueba
            {"$push": {
                "subtemas": {
                    "nombre_subtema": obj.nombre_subtema,
                    "palabras_desafio": []
                }
            }}
        )


@admin.register(PalabraDesafio)
class PalabraDesafioAdmin(admin.ModelAdmin):
    list_display = ('palabra', 'pista')
    search_fields = ('palabra', 'pista')

    def save_model(self, request, obj, form, change):
        """Inyecta una nueva palabra directo en el subtema embebido en Mongo"""
        palabra_limpia = obj.palabra.upper().strip()
        
        # Buscamos el primer subtema del Nivel 1 y le metemos la nueva palabra al sub-arreglo
        db.niveles.update_one(
            {"numero": 1, "subtemas.nombre_subtema": "Reacciones Nucleares"},
            {"$push": {
                "subtemas.$.palabras_desafio": {
                    "palabra": palabra_limpia,
                    "pista": obj.pista
                }
            }}
        )


@admin.register(NivelProgresion)
class NivelProgresionAdmin(admin.ModelAdmin):
    list_display = ('id_nivel_prog', 'id_nivel', 'id_subtema')
