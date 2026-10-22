from pathlib import Path
import pandas as pd

def pregunta_03():
    """
    Usando `data/tbl0.tsv`, cuente cuántos registros hay para cada categoría
    de la columna `c1`. Retorne una Serie de Pandas cuyo índice son las
    categorías, en orden alfabético, y cuyos valores son las cantidades.

    Ejemplo del formato de la respuesta:

        c1
        A     8
        B     7
        C     5
        ...
    """

    file_path = Path("data/tbl0.tsv")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "tbl0.tsv"

    df = pd.read_csv(file_path, sep="\t")
    return df["c1"].value_counts().sort_index()
