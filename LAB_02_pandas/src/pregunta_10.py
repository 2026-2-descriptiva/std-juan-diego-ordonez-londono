from pathlib import Path
import pandas as pd

def pregunta_10():
    """
    Usando `data/tbl0.tsv`, construya para cada categoría de la columna `c1`
    un texto con todos sus valores de la columna `c2`, ordenados de menor a
    mayor y separados por `:`. Retorne un DataFrame cuyo índice son las
    categorías, en orden alfabético, con una única columna llamada `c2`.

    Ejemplo del formato de la respuesta:

                           c2
        c1
        A     1:1:2:3:6:7:8:9
        B       1:3:4:5:6:8:9
        C           0:5:6:7:9
        ...
    """

    file_path = Path("data/tbl0.tsv")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "tbl0.tsv"

    df = pd.read_csv(file_path, sep="\t")

    df = df.sort_values("c2")
    df["c2"] = df["c2"].astype(str)
    resultado = df.groupby("c1")["c2"].apply(":".join)
    resultado = resultado.to_frame()

    return resultado
