from pathlib import Path
import gzip

def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """

    file_path = Path("data/data.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    value_letter = {}
    with gzip.open(file_path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t")
                val = int(parts[1])
                letter = parts[0]
                if val not in value_letter:
                    value_letter[val] = []
                if letter not in value_letter[val]:
                    value_letter[val].append(letter)

    return [(val, sorted(letters)) for val, letters in sorted(value_letter.items())]
