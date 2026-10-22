import json
import re
from pathlib import Path

import pandas as pd

def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    required_columns = [
        "supplier_id",
        "supplier",
        "country",
        "city",
        "purchase_date",
        "amount",
        "discount",
        "weight",
        "units",
        "unit_price",
        "contact_email",
    ]

    df = pd.read_csv("data/ventas.csv.gz", keep_default_na=False)


    df.columns = [
        c.lstrip("\ufeff").strip().lower().replace(" ", "_") for c in df.columns
    ]

    row_count = len(df)
    column_count = len(df.columns)
    missing_required = sorted(c for c in required_columns if c not in df.columns)
    unexpected = sorted(c for c in df.columns if c not in required_columns)

    duplicate_row_count = int(df.duplicated().sum())

    duplicate_supplier_id_row_count = 0
    if "supplier_id" in df.columns:
        duplicate_supplier_id_row_count = int(df["supplier_id"].duplicated(keep=False).sum())

    missing_value_count_by_column = {}
    for col in df.columns:
        valores = df[col].astype(str).str.strip()
        missing_value_count_by_column[col] = int(valores.isin(["", "N/A"]).sum())


    email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    invalid_email_count = 0
    if "contact_email" in df.columns:
        for email in df["contact_email"]:
            if not email_regex.match(str(email).strip()):
                invalid_email_count += 1

  
    invalid_unit_count = 0
    if "units" in df.columns:
        for unidad in df["units"]:
            texto = str(unidad).strip()
            if texto in ["", "N/A"]:
                continue
            try:
                numero = float(texto)
                if not (numero.is_integer() and numero > 0):
                    invalid_unit_count += 1
            except ValueError:
                invalid_unit_count += 1

    country_values = []
    if "country" in df.columns:
        country_values = sorted(df["country"].unique().tolist())


    report = {
        "row_count": row_count,
        "column_count": column_count,
        "missing_required_columns": missing_required,
        "unexpected_columns": unexpected,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    Path("submission").mkdir(parents=True, exist_ok=True)
    with open("submission/data_quality_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report


pregunta_01 = main