from importlib.metadata import files

import pandas as pd
from pathlib import Path

def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
    archivos comprimidos, `data/bank-marketing-campaing-*.csv.gz`, con
    información mezclada del cliente, de la campaña y del contexto económico.
    Su tarea es leerlos directamente desde los archivos comprimidos, sin
    descomprimirlos a mano, y separarlos en tres tablas limpias.

    Guarde cada tabla como un CSV sin comprimir en `submission/`, sin el índice
    de Pandas y con las columnas en el orden indicado:

    1. `client.csv`: `client_id`, `age`, `job`, `marital`, `education`,
       `credit_default` y `mortgage`.
       - En `job`, elimine los puntos y cambie los guiones por guiones bajos.
       - En `education`, cambie los puntos por guiones bajos y deje el valor
         `unknown` como faltante.
       - En `credit_default` y `mortgage`, escriba 1 si el valor es `yes` y 0
         en cualquier otro caso.

    2. `campaign.csv`: `client_id`, `number_contacts`, `contact_duration`,
       `previous_campaign_contacts`, `previous_outcome`, `campaign_outcome` y
       `last_contact_date`.
       - En `previous_outcome`, escriba 1 si el valor es `success` y 0 en
         cualquier otro caso.
       - En `campaign_outcome`, escriba 1 si el valor es `yes` y 0 en
         cualquier otro caso.
       - Construya `last_contact_date` a partir de las columnas `month` y
         `day`, usando el año 2022 y el formato `AAAA-MM-DD`.

    3. `economics.csv`: `client_id`, `cons_price_idx` y
       `euribor_three_months`.

    La función también debe retornar las tres tablas, en el orden `client`,
    `campaign` y `economics`.

    Ejemplo del formato de `campaign.csv`:

        client_id,number_contacts,contact_duration,...,last_contact_date
        0,1,261,...,2022-05-13
        ...
    """

    data_dir = Path("data")
    if not (data_dir / "bank-marketing-campaing-0.csv.gz").exists():
        data_dir = Path(__file__).resolve().parent.parent / "data"
        submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
        submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(data_dir.glob("bank-marketing-campaing-*.csv.gz"))
    parts = []
    for f in files:
        parts.append(pd.read_csv(f, compression="gzip"))
    df = pd.concat(parts, ignore_index=True)

    # 1. client
    client = pd.DataFrame({
        "client_id": df["client_id"].astype(int),
        "age": df["age"].astype(int),
        "job": df["job"].str.replace(".", "", regex=False).str.replace("-", "_", regex=False),
        "marital": df["marital"],
        "education": df["education"].str.replace(".", "_", regex=False).replace("unknown", pd.NA),
        "credit_default": (df["credit_default"] == "yes").astype(int),
        "mortgage": (df["mortgage"] == "yes").astype(int),
    })

    # 2. campaign
    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }
    month_num = df["month"].str.lower().map(months)
    day_num = df["day"].astype(str).str.zfill(2)
    date = pd.to_datetime({"year": 2022, "month": month_num, "day": day_num})
    last_contact_date = date.dt.strftime("%Y-%m-%d")

    campaign = pd.DataFrame({
        "client_id": df["client_id"].astype(int),
        "number_contacts": df["number_contacts"].astype(int),
        "contact_duration": df["contact_duration"].astype(int),
        "previous_campaign_contacts": df["previous_campaign_contacts"].astype(int),
        "previous_outcome": (df["previous_outcome"] == "success").astype(int),
        "campaign_outcome": (df["campaign_outcome"] == "yes").astype(int),
        "last_contact_date": last_contact_date,
    })

    # 3. economics
    economics = pd.DataFrame({
        "client_id": df["client_id"].astype(int),
        "cons_price_idx": df["cons_price_idx"].astype(float),
        "euribor_three_months": df["euribor_three_months"].astype(float),
    })

    client.to_csv(submission_dir / "client.csv", index=False)
    campaign.to_csv(submission_dir / "campaign.csv", index=False)
    economics.to_csv(submission_dir / "economics.csv", index=False)

    return client, campaign, economics
