from pathlib import Path

import pandas as pd
def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """

    data_dir = Path("data")
    if not (data_dir / "train").exists():
        data_dir = Path(__file__).resolve().parent.parent / "data"
        submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
        submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    for split in ["train", "test"]:
        records = []
        split_dir = data_dir / split
        categories = sorted([d.name for d in split_dir.iterdir() if d.is_dir()])
        for cat in categories:
            cat_dir = split_dir / cat
            txt_files = sorted(cat_dir.glob("*.txt"))
            for f in txt_files:
                content = f.read_text(encoding="utf-8").strip()
                records.append({"phrase": content, "target": cat})

        df = pd.DataFrame(records)
        df.to_csv(submission_dir / f"{split}_dataset.csv", index=False)

