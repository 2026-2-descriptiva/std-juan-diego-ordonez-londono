from pathlib import Path
import gzip

def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """
    file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    valores = {}

    with gzip.open(file_path, "rt", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue
            columnas = linea.split("\t")
            if valores.get(columnas[0]) is None:
                valores[columnas[0]] = []
            valores[columnas[0]].append(int(columnas[1]))

    return [(letra, max(v), min(v)) for letra, v in sorted(valores.items())]

print(pregunta_05())
