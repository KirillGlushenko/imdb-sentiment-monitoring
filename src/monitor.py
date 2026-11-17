
import logging
from pathlib import Path

import pandas as pd
from notifier import send_telegram, send_email


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "imdb_clean.csv"
LOG_PATH = BASE_DIR / "logs" / "monitor.log"

BATCH_SIZE = 100
MAX_BATCHES = 5
NEGATIVE_THRESHOLD = 40.0


# Настройка логирования
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)


def analyze_batch(batch, batch_number):
    total = len(batch)

    if total == 0:
        return

    positive = (batch["sentiment"] == "positive").sum()
    negative = (batch["sentiment"] == "negative").sum()

    negative_percent = negative / total * 100

    print(f"\nПартия №{batch_number}")
    print(f"Всего отзывов: {total}")
    print(f"Положительных: {positive}")
    print(f"Отрицательных: {negative}")
    print(f"Доля негатива: {negative_percent:.2f}%")

    logger.info(
        "Партия %s: всего=%s, positive=%s, negative=%s, "
        "доля негатива=%.2f%%",
        batch_number,
        total,
        positive,
        negative,
        negative_percent
    )

    if negative_percent > NEGATIVE_THRESHOLD:
        message = (
            f"IMDb ALERT! Партия №{batch_number}\n"
            f"Всего отзывов: {total}\n"
            f"Негативных: {negative}\n"
            f"Доля негатива: {negative_percent:.2f}%\n"
            f"Порог: {NEGATIVE_THRESHOLD}%"
        )

        print("ВНИМАНИЕ! Высокая доля негатива!")
        logger.warning(
            "Превышен порог негатива в партии №%s: %.2f%%",
            batch_number,
            negative_percent
        )

        send_telegram(message)
        send_email("IMDb Sentiment Alert", message)

    else:
        print("Ситуация в норме.")
        logger.info("Партия №%s: ситуация в норме", batch_number)


def main():
    print("Запуск мониторинга IMDb...")
    logger.info("Мониторинг IMDb запущен")

    if not DATA_PATH.exists():
        print(f"Ошибка: файл не найден: {DATA_PATH}")
        logger.error("Файл данных не найден: %s", DATA_PATH)
        return

    try:
        df = pd.read_csv(DATA_PATH)

        required_columns = {"review", "sentiment"}

        if not required_columns.issubset(df.columns):
            print("Ошибка: отсутствуют необходимые столбцы.")
            logger.error("Отсутствуют обязательные столбцы")
            return

        print(f"Загружено отзывов: {len(df)}")
        logger.info("Загружено отзывов: %s", len(df))

        for i in range(MAX_BATCHES):
            start = i * BATCH_SIZE
            end = start + BATCH_SIZE

            batch = df.iloc[start:end]

            if batch.empty:
                break

            analyze_batch(batch, i + 1)

        print("\nМониторинг завершён.")
        logger.info("Мониторинг завершён")

    except Exception:
        logger.exception("Ошибка при мониторинге")
        raise


if __name__ == "__main__":
    main()
