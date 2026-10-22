
from pathlib import Path
import pandas as pd

def pregunta_06():
    """
    Usando `data/tbl1.tsv`, obtenga los valores distintos de la columna `c4`,
    conviértalos a mayúsculas y retórnelos como una lista ordenada
    alfabéticamente.

    Ejemplo del formato de la respuesta:

        ["A", "B", "C", "D", "E", "F", "G"]
    """

    file_path = Path("data/tbl1.tsv")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "tbl1.tsv"

    df = pd.read_csv(file_path, sep="\t")
    letters = set(df["c4"].str.upper())
    return sorted(list(letters))
