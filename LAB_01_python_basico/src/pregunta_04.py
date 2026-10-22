
import gzip
from pathlib import Path

def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """

    file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    conteo = {}

    with gzip.open(file_path, "rt", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:
                continue
            mes = linea.split("\t")[2].split("-")[1]
            if mes not in conteo:
                conteo[mes] = 0
            conteo[mes] += 1

    return sorted(conteo.items())