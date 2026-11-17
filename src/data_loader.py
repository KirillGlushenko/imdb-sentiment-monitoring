from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"review", "sentiment"}

def load_reviews(path: str | Path) -> pd.DataFrame:
    """Load IMDb reviews from CSV or a ZIP containing one CSV."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Файл не найден: {path}\n"
            "Положи archive.zip или IMDB Dataset.csv в папку data/raw."
        )

    df = pd.read_csv(path, compression="infer")
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"В датасете отсутствуют обязательные колонки: {sorted(missing)}")

    return df[["review", "sentiment"]].copy()
