import random
import string

def generar_sopa(palabras, tamaño=15):
    tablero = [['' for _ in range(tamaño)] for _ in range(tamaño)]
    direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    # Ordenar por tamaño para maximizar cruces
    palabras_limpias = sorted([p.upper().strip() for p in palabras], key=len, reverse=True)

    for palabra in palabras_limpias:
        colocada = False
        intentos = 0
        while not colocada and intentos < 2000:
            df, dc = random.choice(direcciones)
            f = random.randint(0, tamaño - 1)
            c = random.randint(0, tamaño - 1)

            fin_f = f + df * (len(palabra) - 1)
            fin_c = c + dc * (len(palabra) - 1)

            if 0 <= fin_f < tamaño and 0 <= fin_c < tamaño:
                puede_colocar = True
                cruces = 0
                for i in range(len(palabra)):
                    char_tablero = tablero[f + i*df][c + i*dc]
                    if char_tablero != '' and char_tablero != palabra[i]:
                        puede_colocar = False
                        break
                    if char_tablero == palabra[i]: cruces += 1
                
                if puede_colocar:
                    for i in range(len(palabra)):
                        tablero[f + i*df][c + i*dc] = palabra[i]
                    colocada = True
            intentos += 1

    for f in range(tamaño):
        for c in range(tamaño):
            if tablero[f][c] == '':
                tablero[f][c] = random.choice(string.ascii_uppercase)
    return tablero
