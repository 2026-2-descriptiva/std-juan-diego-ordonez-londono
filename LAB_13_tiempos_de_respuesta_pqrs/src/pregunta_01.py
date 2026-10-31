from pathlib import Path

import numpy as np
import pandas as pd

DIAS_SEMANA = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PLAZO_DIAS_HABILES = 15


def obtener_rutas() -> tuple[Path, Path]:
    """Busca la carpeta de datos y crea la carpeta de entrega."""
    data_dir = Path("data")
    submission_dir = Path("submission")

    if not (data_dir / "historical_requests_web.csv.gz").exists():
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"
        submission_dir = base_dir / "submission"

    submission_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, submission_dir


def cargar_canal(path: Path, channel: str) -> pd.DataFrame:
    """Lee un canal, quita las filas repetidas y le pone el nombre del canal."""
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    df["channel"] = channel
    return df


def contar_dias_habiles(in_dt: pd.Series, out_dt: pd.Series) -> np.ndarray:
    """
    Cuenta los días de lunes a viernes después de la entrada, hasta la
    respuesta incluida. busday_count no incluye el último día, por eso se le
    suma 1 día a las dos fechas.
    """
    un_dia = np.timedelta64(1, "D")
    inicio = in_dt.values.astype("datetime64[D]") + un_dia
    fin = out_dt.values.astype("datetime64[D]") + un_dia
    dias = np.busday_count(inicio, fin)
    return dias


def preparar_datos(data_dir: Path) -> pd.DataFrame:
    """Une los dos canales y calcula los días de respuesta de cada solicitud."""
    df_letter = cargar_canal(data_dir / "historical_requests_letter.csv.gz", "letter")
    df_web = cargar_canal(data_dir / "historical_requests_web.csv.gz", "web")
    df = pd.concat([df_letter, df_web], ignore_index=True)

    in_dt = pd.to_datetime(df["in_date"])
    out_dt = pd.to_datetime(df["out_date"])

    df["year"] = in_dt.dt.year
    df["answered"] = out_dt.notna()
    df["calendar_days"] = (out_dt - in_dt).dt.days

    respondidas = df["answered"]
    dias_habiles = contar_dias_habiles(in_dt[respondidas], out_dt[respondidas])
    df["business_days"] = np.nan
    df.loc[respondidas, "business_days"] = dias_habiles
    df["on_time"] = df["business_days"] <= PLAZO_DIAS_HABILES
    return df


def resumen_por_canal(df: pd.DataFrame) -> pd.DataFrame:
    grupos = df.groupby("channel")

    resumen = pd.DataFrame()
    resumen["requests"] = grupos.size()
    resumen["answered"] = grupos["answered"].sum()
    resumen["pending"] = resumen["requests"] - resumen["answered"]
    resumen["median_business_days"] = grupos["business_days"].median()
    resumen["on_time_rate"] = grupos["on_time"].mean()

    resumen = resumen.reset_index()
    return resumen


def resumen_por_anio(df: pd.DataFrame) -> pd.DataFrame:
    grupos = df.groupby(["year", "channel"])

    resumen = pd.DataFrame()
    resumen["requests"] = grupos.size()
    resumen["pending"] = resumen["requests"] - grupos["answered"].sum()
    resumen["on_time_rate"] = grupos["on_time"].mean()

    resumen = resumen.reset_index()
    return resumen


def resumen_por_dia(df: pd.DataFrame) -> pd.DataFrame:
    grupos = df.groupby("day_name")

    resumen = pd.DataFrame()
    resumen["requests"] = grupos.size()
    resumen["median_calendar_days"] = grupos["calendar_days"].median()
    resumen["median_business_days"] = grupos["business_days"].median()
    resumen = resumen.reindex(DIAS_SEMANA)
    resumen.index.name = "day_name"
    resumen = resumen.reset_index()
    return resumen

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """

    data_dir, submission_dir = obtener_rutas()

    df = preparar_datos(data_dir)

    channel_summary = resumen_por_canal(df)
    yearly_summary = resumen_por_anio(df)
    entry_day_summary = resumen_por_dia(df)

    channel_summary.to_csv(submission_dir / "channel_summary.csv", index=False)
    yearly_summary.to_csv(submission_dir / "yearly_summary.csv", index=False)
    entry_day_summary.to_csv(submission_dir / "entry_day_summary.csv", index=False)

    return channel_summary, yearly_summary, entry_day_summary