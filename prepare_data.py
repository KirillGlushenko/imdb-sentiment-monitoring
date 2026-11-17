from pathlib import Path
from src.data_loader import load_reviews
from src.data_processor import prepare_reviews

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "data" / "raw" / "archive.zip"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "imdb_clean.csv"

def main():
    print("Загрузка исходного датасета...")
    raw_df = load_reviews(INPUT_PATH)
    print(f"Исходный размер: {len(raw_df)} строк")

    print("Очистка и проверка данных...")
    clean_df = prepare_reviews(raw_df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"Готово. Файл сохранён: {OUTPUT_PATH}")
    print("\nРаспределение тональности:")
    print(clean_df["sentiment"].value_counts())
    print("\nПустые значения:")
    print(clean_df.isna().sum())

if __name__ == "__main__":
    main()
