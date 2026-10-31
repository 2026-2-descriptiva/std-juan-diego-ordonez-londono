from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """
    file_path = Path("data/sales.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "sales.csv.gz"
        submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
        submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_path)

    order_date = pd.to_datetime(df["OrderDate"])
    df["order_period"] = order_date.dt.to_period("M")
    df["cohort_period"] = df.groupby("CustomerID")["order_period"].transform("min")

    df["cohort_month"] = df["cohort_period"].astype(str)
    df["period_index"] = (
        (df["order_period"].dt.year - df["cohort_period"].dt.year) * 12
        + (df["order_period"].dt.month - df["cohort_period"].dt.month)
    )

    cohort_sizes = df.groupby("cohort_month")["CustomerID"].nunique().to_dict()

    cohort_data = (
        df.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .reset_index()
        .rename(columns={"CustomerID": "active_customers"})
        .sort_values(["cohort_month", "period_index"])
        .reset_index(drop=True)
    )
    cohort_data["cohort_size"] = cohort_data["cohort_month"].map(cohort_sizes)
    cohort_data["retention_rate"] = cohort_data["active_customers"] / cohort_data["cohort_size"]

    cols = ["cohort_month", "period_index", "active_customers", "cohort_size", "retention_rate"]
    cohort_data = cohort_data[cols]
    cohort_data.to_csv(submission_dir / "cohort_retention.csv", index=False)

    # Heatmap
    retention_matrix = cohort_data.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(retention_matrix, cmap="Blues", vmin=0, vmax=1)

    ax.set_xticks(range(len(retention_matrix.columns)))
    ax.set_xticklabels(retention_matrix.columns)
    ax.set_yticks(range(len(retention_matrix.index)))
    ax.set_yticklabels(retention_matrix.index)

    ax.set_xlabel("period_index")
    ax.set_ylabel("cohort_month")
    ax.set_title("Cohort Retention Heatmap")

    for i in range(len(retention_matrix.index)):
        for j in range(len(retention_matrix.columns)):
            val = retention_matrix.iloc[i, j]
            if pd.notna(val):
                text_color = "white" if val > 0.5 else "black"
                ax.text(
                    j, i, f"{val:.1%}",
                    ha="center", va="center", color=text_color, fontsize=9
                )

    plt.colorbar(im, ax=ax, label="retention_rate")
    plt.tight_layout()
    fig.savefig(submission_dir / "cohort_retention_heatmap.png")
    plt.close(fig)

    return cohort_data


pregunta_01 = build_cohort_analysis


