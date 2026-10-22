from pathlib import Path
import gzip

def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
    file_path = Path("data/data.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    letter_sums = {}
    with gzip.open(file_path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t")
                letter = parts[0]
                metrics=parts[4].split(",")
                metrics_sum=0
                for pair in metrics:
                    metrics_sum+=int(pair.split(":")[1])
                if letter not in letter_sums:
                    letter_sums[letter] = 0
                letter_sums[letter] += metrics_sum

    return dict(sorted(letter_sums.items()))