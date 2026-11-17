# Título: Proyecto 3 - Interfaz Web con Streamlit (main.py)
# Autor: Diego Vázquez Hernández
# Fecha: 16/11/2026
# Descripción: Menú de consola del Proyecto 2 para la red de transporte.
"""
Objetivo: Agregar conexiones a nodos.csv y calcular la ruta más corta con
    Dijkstra desde la terminal, reutilizando grafo.py e io_handler.py.

Ejecución: python main.py
"""

from grafo import Grafo
from io_handler import (
    cargar_grafo,
    formatear_peso,
    guardar_arista,
    normalizar_nodo,
    validar_peso,
)

MENU: str = """
========== RED DE TRANSPORTE ==========
1. Agregar conexión
2. Calcular ruta más corta
3. Mostrar red
4. Salir
"""


def agregar_conexion(grafo: Grafo) -> None:
    """Pide una conexión, la guarda en el CSV y la agrega al grafo."""
    try:
        origen = normalizar_nodo(input("Nodo origen: "))
        destino = normalizar_nodo(input("Nodo destino: "))
        if origen == destino:
            raise ValueError("El destino debe ser distinto al origen.")
        peso = validar_peso(input("Peso: "))
        guardar_arista(origen, destino, peso)
    except ValueError as error:
        print(f"  [Error] {error}")
    except PermissionError:
        print("  [Error] No hay permiso para escribir en nodos.csv.")
    except OSError as error:
        print(f"  [Error] No se pudo guardar en el archivo: {error}")
    else:
        # Se actualiza la memoria sin volver a leer el CSV
        grafo.agregar_arista(origen, destino, peso)
        print(f"  Conexión guardada: {origen} <-> {destino} "
              f"(peso {formatear_peso(peso)}).")


def calcular_ruta(grafo: Grafo) -> None:
    """Pide origen y destino y muestra la ruta más corta."""
    try:
        inicio = normalizar_nodo(input("Nodo de inicio: "))
        destino = normalizar_nodo(input("Nodo destino: "))
        for nombre in (inicio, destino):
            if nombre not in grafo.nodos:
                raise KeyError(nombre)
        distancia, camino = grafo.dijkstra(inicio, destino)
    except ValueError as error:
        print(f"  [Error] {error}")
        return
    except KeyError as error:
        print(f"  [Error] El nodo '{error.args[0]}' no existe en la red.")
        return

    if not camino:
        print(f"  No existe una ruta entre {inicio} y {destino}.")
        return
    print(f"  Ruta: {' -> '.join(camino)}")
    print(f"  Peso total: {formatear_peso(distancia)}")


def mostrar_red(grafo: Grafo) -> None:
    """Imprime todas las conexiones registradas."""
    conexiones = grafo.conexiones()
    if not conexiones:
        print("  La red está vacía.")
        return
    print(f"  {'Origen':<10}{'Destino':<10}Peso")
    for origen, destino, peso in conexiones:
        print(f"  {origen:<10}{destino:<10}{formatear_peso(peso)}")


def main() -> None:
    """Carga el grafo una vez y atiende el menú hasta que se elija salir."""
    grafo = cargar_grafo()
    opciones = {
        "1": agregar_conexion,
        "2": calcular_ruta,
        "3": mostrar_red,
    }

    while True:
        print(MENU)
        try:
            opcion = input("Elige una opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if opcion == "4":
            print("Saliendo...")
            break
        accion = opciones.get(opcion)
        if accion is None:
            print("  [Error] Opción no válida, elige del 1 al 4.")
            continue
        try:
            accion(grafo)
        except (EOFError, KeyboardInterrupt):
            print("\n  Operación cancelada.")


if __name__ == "__main__":
    main()
