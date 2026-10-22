
from pathlib import Path
import pandas as pd

def pregunta_01():
    """
    ¿Cuántos registros tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        40
    """

    file_path = Path("data/tbl0.tsv")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "tbl0.tsv"

    df = pd.read_csv(file_path, sep="\t")
    return len(df)