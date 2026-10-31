from pathlib import Path
import pandas as pd

def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """
    def clean_text(df, values):
        for col in values:
          df[col] = (
              df[col]
              .astype(str)
              .str.lower()
              .str.replace("-", " ", regex=False)
              .str.replace("_", " ", regex=False)
              .str.split()
              .str.join(" ")
          )

    def clean_date(val):
        s = str(val).strip().replace("-", "/")
        parts = s.split("/")
        if len(parts) == 3:
            if len(parts[0]) == 4:
                year, month, day = parts[0], parts[1], parts[2]
            else:
                day, month, year = parts[0], parts[1], parts[2]
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        return val

    def clean_monto(val):
        s = str(val).replace("$", "").replace(",", "").strip()
        return int(float(s))


    file_path = Path("data/solicitudes_de_credito.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "solicitudes_de_credito.csv.gz"
        submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
        submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_path, sep=";", index_col=0, encoding="utf-8")

    columns = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "comuna_ciudadano",
        "fecha_de_beneficio",
        "monto_del_credito",
        "línea_credito",
    ]

    text_columns = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "comuna_ciudadano",
        "línea_credito",
    ]
    
    df.columns = columns

    column_not_comuna = [c for c in df.columns if c != "comuna_ciudadano"]
    df = df.dropna(subset=column_not_comuna).copy()

    clean_text(df, text_columns)

    df["estrato"] = df["estrato"].astype(int)

    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].apply(clean_date)

    df["monto_del_credito"] = df["monto_del_credito"].apply(clean_monto)

    df = df.drop_duplicates()

    df.to_csv(submission_dir / "solicitudes_de_credito.csv", sep=";", index=False)