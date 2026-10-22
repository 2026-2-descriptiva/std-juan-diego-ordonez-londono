import re
from pathlib import Path
import pandas as pd

ROW_PATTERN = re.compile(r"^\s*(\d+)\s+(\d+)\s+([\d,]+)\s*%\s+(.*)$")


def _resolve_path() -> Path:
  path = Path("data/clusters_report.txt")
  if path.exists():
      return path
  return Path(__file__).resolve().parent.parent / "data" / "clusters_report.txt"


def _parse_clusters(lines):
  current = None
  for line in lines:
      match = ROW_PATTERN.match(line)
      if match:
          if current:
              yield current
          cluster, cantidad, porcentaje, words = match.groups()
          current = {
              "cluster": int(cluster),
              "cantidad_de_palabras_clave": int(cantidad),
              "porcentaje_de_palabras_clave": float(porcentaje.replace(",", ".")),
              "words": [words],
          }
      elif current and line.strip():
          current["words"].append(line)
  if current:
      yield current


def _join_keywords(chunks) -> str:
  text = " ".join(" ".join(chunks).split())
  return text.removesuffix(".").strip()

def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """
    with open(_resolve_path(), encoding="utf-8") as f:
        records = [
            {
                "cluster": c["cluster"],
                "cantidad_de_palabras_clave": c["cantidad_de_palabras_clave"],
                "porcentaje_de_palabras_clave": c["porcentaje_de_palabras_clave"],
                "principales_palabras_clave": _join_keywords(c["words"]),
            }
            for c in _parse_clusters(f)
        ]
    return pd.DataFrame(records)
