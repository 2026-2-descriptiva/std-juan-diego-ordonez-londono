from pathlib import Path
import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Una autoridad aeronáutica publica cada año un ranking de aerolíneas según
    su tasa de demora, y algunas aerolíneas se quejan de que es injusto: las
    demoras se acumulan a lo largo del día, de modo que una aerolínea con
    muchos vuelos en la tarde y la noche parece peor aunque opere igual de
    bien que las demás. Su tarea es construir un ranking que tenga en cuenta
    la mezcla de horarios de cada aerolínea.

    El archivo `data/flights_by_carrier_day_hour.csv.gz` tiene los vuelos
    nacionales entre 2006 y 2008, agregados por año, mes, día de la semana,
    hora programada de salida (`scheduled_departure_hour`) y aerolínea
    (`reporting_airline`). Use las columnas `operated_flights` (vuelos
    operados) y `delayed_departure_15_flights` (vuelos que salieron con 15
    minutos o más de demora).

    Siga estos pasos:

    1. Calcule la tasa nacional de demora de cada hora programada de salida:
       vuelos demorados sobre vuelos operados, con todas las aerolíneas
       juntas.
    2. Para cada aerolínea, calcule las demoras esperadas: en cada hora,
       multiplique sus vuelos operados por la tasa nacional de esa hora, y
       sume sobre todas las horas. Son las demoras que tendría si en cada hora
       se comportara como el promedio nacional.
    3. Divida las demoras observadas entre las esperadas. Un valor mayor que 1
       significa que la aerolínea se demora más de lo que explican sus
       horarios.

    Genere dos archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `hourly_delay_rates.csv`, con una fila por hora, de 0 a 23:
       `scheduled_departure_hour`, `operated_flights`,
       `delayed_departure_15_flights` y `delay_rate`.

    2. `carrier_adjusted_delays.csv`, con una fila por aerolínea:
       `reporting_airline`, `operated_flights`,
       `delayed_departure_15_flights`, `delay_rate` (la tasa sin ajustar),
       `expected_delayed_flights`, `observed_to_expected_ratio`, `crude_rank`
       y `adjusted_rank`. Incluya solamente aerolíneas con al menos 100 000
       vuelos operados. `crude_rank` es la posición según `delay_rate` y
       `adjusted_rank` la posición según `observed_to_expected_ratio`; en
       ambos, 1 es la peor aerolínea. Ordene la tabla por `adjusted_rank`.

    Compare los dos rankings: las aerolíneas que cambian de posición son las
    que el ranking sin ajustar juzga mal por sus horarios.

    La función también debe retornar las dos tablas, en el mismo orden.

    Ejemplo del formato de `carrier_adjusted_delays.csv`:

        reporting_airline,operated_flights,...,crude_rank,adjusted_rank
        EV,819223,...,1,1
        ...
    """

    file_path = Path("data/flights_by_carrier_day_hour.csv.gz")
    if not file_path.exists():
      file_path = Path(__file__).resolve().parent.parent / "data" / "flights_by_carrier_day_hour.csv.gz"
      submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
      submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_path)

    hourly = (
      df.groupby("scheduled_departure_hour")[["operated_flights", "delayed_departure_15_flights"]]
      .sum()
      .reset_index()
      .sort_values("scheduled_departure_hour")
      .reset_index(drop=True)
    )
    hourly["delay_rate"] = hourly["delayed_departure_15_flights"] / hourly["operated_flights"]

    # 2. Carrier adjusted delays
    rate_map = hourly.set_index("scheduled_departure_hour")["delay_rate"].to_dict()
    df["hourly_delay_rate"] = df["scheduled_departure_hour"].map(rate_map)
    df["expected_delays"] = df["operated_flights"] * df["hourly_delay_rate"]

    carrier = (
      df.groupby("reporting_airline")
      .agg({
            "operated_flights": "sum",
            "delayed_departure_15_flights": "sum",
            "expected_delays": "sum",
      })
      .reset_index()
    )
    carrier = carrier[carrier["operated_flights"] >= 100000].copy()
    carrier.rename(columns={"expected_delays": "expected_delayed_flights"}, inplace=True)
    carrier["delay_rate"] = carrier["delayed_departure_15_flights"] / carrier["operated_flights"]
    carrier["observed_to_expected_ratio"] = carrier["delayed_departure_15_flights"] / carrier["expected_delayed_flights"]

    carrier["crude_rank"] = carrier["delay_rate"].rank(ascending=False).astype(int)
    carrier["adjusted_rank"] = carrier["observed_to_expected_ratio"].rank(ascending=False).astype(int)

    carrier = carrier.sort_values("adjusted_rank").reset_index(drop=True)

    hourly_cols = [
      "scheduled_departure_hour",
      "operated_flights",
      "delayed_departure_15_flights",
      "delay_rate",
    ]
    carrier_cols = [
      "reporting_airline",
      "operated_flights",
      "delayed_departure_15_flights",
      "delay_rate",
      "expected_delayed_flights",
      "observed_to_expected_ratio",
      "crude_rank",
      "adjusted_rank",
    ]

    hourly = hourly[hourly_cols]
    carrier = carrier[carrier_cols]

    hourly.to_csv(submission_dir / "hourly_delay_rates.csv", index=False)
    carrier.to_csv(submission_dir / "carrier_adjusted_delays.csv", index=False)

    return hourly, carrier


