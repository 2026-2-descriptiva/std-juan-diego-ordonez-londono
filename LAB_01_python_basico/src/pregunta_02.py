import gzip
from pathlib import Path

def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """

    file_path = Path("data/data.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"


    conteo = {}

    with gzip.open(file_path, "rt", encoding="utf-8") as archivo:
        for renglon in archivo:
            renglon = renglon.strip()
            if not renglon:
                continue
            letra = renglon.split(",")[0][0]
            conteo[letra] = conteo.get(letra, 0) + 1

    return sorted(conteo.items())

print(pregunta_02())
