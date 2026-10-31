from pathlib import Path
import pandas as pd
def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """
    file_path = Path("data/superstore_orders.csv.gz")
    if not file_path.exists():
      file_path = Path(__file__).resolve().parent.parent / "data" / "superstore_orders.csv.gz"
      submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
      submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_path, sep=";", decimal=",")

    lines = int(len(df))
    orders = int(df["Order ID"].nunique())
    sales = float(df["Sales"].sum())
    profit = float(df["Profit"].sum())
    profit_margin = profit / sales if sales != 0 else 0.0
    loss_mask = df["Profit"] < 0
    loss_lines = int(loss_mask.sum())
    loss_line_rate = loss_lines / lines if lines != 0 else 0.0
    lost_profit = float(df.loc[loss_mask, "Profit"].abs().sum())

    profitability_summary = pd.DataFrame([{
      "lines": lines,
      "orders": orders,
      "sales": sales,
      "profit": profit,
      "profit_margin": profit_margin,
      "loss_lines": loss_lines,
      "loss_line_rate": loss_line_rate,
      "lost_profit": lost_profit,
   }])

    def get_band(d):
      if d == 0:
         return "0%"
      elif d <= 0.05:
         return "1%-5%"
      elif d <= 0.10:
         return "6%-10%"
      else:
         return "más de 10%"

    df["discount_band"] = df["Discount"].apply(get_band)
    band_order = ["0%", "1%-5%", "6%-10%", "más de 10%"]

    t2_rows = []
    for b in band_order:
      sub = df[df["discount_band"] == b]
      b_lines = int(len(sub))
      b_sales = float(sub["Sales"].sum())
      b_profit = float(sub["Profit"].sum())
      b_margin = b_profit / b_sales if b_sales != 0 else 0.0
      b_loss_mask = sub["Profit"] < 0
      b_loss_lines = int(b_loss_mask.sum())
      b_rate = b_loss_lines / b_lines if b_lines != 0 else 0.0
      b_lost = float(sub.loc[b_loss_mask, "Profit"].abs().sum())
      t2_rows.append({
         "discount_band": b,
         "lines": b_lines,
         "sales": b_sales,
         "profit": b_profit,
         "profit_margin": b_margin,
         "loss_line_rate": b_rate,
         "lost_profit": b_lost,
      })
    discount_summary = pd.DataFrame(t2_rows)

    t3_rows = []
    for (seg, cat), sub in df.groupby(["Customer Segment", "Product Category"]):
      s_lines = int(len(sub))
      if s_lines < 100:
         continue
      s_sales = float(sub["Sales"].sum())
      s_profit = float(sub["Profit"].sum())
      s_margin = s_profit / s_sales if s_sales != 0 else 0.0
      s_loss_mask = sub["Profit"] < 0
      s_lost = float(sub.loc[s_loss_mask, "Profit"].abs().sum())
      t3_rows.append({
         "Customer Segment": seg,
         "Product Category": cat,
         "lines": s_lines,
         "sales": s_sales,
         "profit": s_profit,
         "profit_margin": s_margin,
         "lost_profit": s_lost,
      })
    priority_segments = (
      pd.DataFrame(t3_rows)
      .sort_values("lost_profit", ascending=False)
      .head(5)
      .reset_index(drop=True)
   )

    profitability_summary.to_csv(submission_dir / "profitability_summary.csv", index=False)
    discount_summary.to_csv(submission_dir / "discount_summary.csv", index=False)
    priority_segments.to_csv(submission_dir / "priority_segments.csv", index=False)

    return profitability_summary, discount_summary, priority_segments


