import gzip
from pathlib import Path

def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """
    file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    suma = {}

    with gzip.open(file_path, "rt", encoding="utf-8") as archivo:
        for renglon in archivo:
            renglon = renglon.strip()
            if not renglon:
                continue
            columnas = renglon.split("\t")
            letra = columnas[0][0]
            valor = int(columnas[1])
            suma[letra] = suma.get(letra, 0) + valor

    return sorted(suma.items())

print(pregunta_03())
