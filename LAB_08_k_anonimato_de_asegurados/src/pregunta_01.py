import pandas as pd
from pathlib import Path
import json

def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    file_path = Path("data/insurance.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "insurance.csv.gz"
        submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
        submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_path)

    #Columnas auxiliares

    def age_group(age):
        if age < 30:
            return "18-29"
        if age < 40:
            return "30-39"
        if age < 50:
            return "40-49"
        return "50-64"

    def bmi_group(bmi):
        if bmi < 18.5:
            return "bajo peso"
        if bmi < 25:
            return "normal"
        if bmi < 30:
            return "sobrepeso"
        return "obesidad"

    def kids_group(kids):
        if kids == 0:
            return "0"
        if kids <= 2:
            return "1-2"
        return "3+"

    df["age_group"] = df["age"].apply(age_group)
    df["bmi_group"] = df["bmi"].apply(bmi_group)
    df["children_group"] = df["children"].apply(kids_group)
    df["es_fumador"] = (df["smoker"] == "yes").astype(int)

    k = 5

    #Riesgo con los cuasi-identificadores originales 

    og_qis = ["age", "sex", "bmi", "children", "region"]
    og_sizes = df.groupby(og_qis)["age"].transform("size")
    og_K = int(og_sizes.min())
    original_unique_records = int((og_sizes == 1).sum())

    #Esquemas de generalización

    schemes = {
        "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
        "without_children": ["age_group", "sex", "bmi_group", "region"],
    }

    schemes_results = {}
    published_dfs = {}

    for name, qis in schemes.items():
        og_sizes = df.groupby(qis)["age"].transform("size")
        published = og_sizes >= k
        df_pub = df[published]

        clases = df.groupby(qis).size()
        clases_pub = df_pub.groupby(qis)["es_fumador"].agg(["size", "sum"])

        smokes = clases_pub["sum"] == clases_pub["size"]
        not_smoke = clases_pub["sum"] == 0
        no_div_records = clases_pub[smokes | not_smoke]

        schemes_results[name] = {
            "quasi_identifiers": qis,
            "equivalence_classes": int(len(clases)),
            "k_before_suppression": int(clases.min()),
            "suppressed_records": int((~published).sum()),
            "published_records": int(published.sum()),
            "published_classes": int(len(clases_pub)),
            "classes_without_smoker_diversity": int(len(no_div_records)),
            "records_without_smoker_diversity": int(no_div_records["size"].sum()),
        }
        published_dfs[name] = published

    # Esquema seleccionado: el que suprime menos registros
    selected_scheme = "with_children"
    if (
        schemes_results["without_children"]["suppressed_records"]
        < schemes_results["with_children"]["suppressed_records"]
    ):
        selected_scheme = "without_children"

    df_published = df[published_dfs[selected_scheme]]

    report = {
        "original_k": og_K,
        "original_unique_records": original_unique_records,
        "schemes": schemes_results,
        "selected_scheme": selected_scheme,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(df_published["charges"].mean()),
        "smoker_rate_original": float(df["es_fumador"].mean()),
        "smoker_rate_published": float(df_published["es_fumador"].mean()),
    }

    Path("submission").mkdir(parents=True, exist_ok=True)

    with open("submission/privacy_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    output_columns = schemes[selected_scheme] + ["smoker", "charges"]
    df_published[output_columns].to_csv(
        "submission/insurance_published.csv", index=False
    )

    return report