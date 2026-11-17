import html
import re
import pandas as pd

VALID_SENTIMENTS = {"positive", "negative"}

def clean_review(text: str) -> str:
    """Remove HTML markup and normalize whitespace in a review."""
    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def prepare_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Validate, clean and deduplicate the source reviews."""
    result = df.copy()

    result["review"] = result["review"].fillna("").astype(str)
    result["sentiment"] = result["sentiment"].fillna("").astype(str).str.strip().str.lower()

    invalid = sorted(set(result["sentiment"].unique()) - VALID_SENTIMENTS)
    if invalid:
        raise ValueError(f"Обнаружены неизвестные значения sentiment: {invalid}")

    result["clean_review"] = result["review"].map(clean_review)
    result = result[result["clean_review"].ne("")].copy()

    before = len(result)
    result = result.drop_duplicates(subset=["clean_review", "sentiment"]).reset_index(drop=True)
    removed_duplicates = before - len(result)

    result["review_length"] = result["clean_review"].str.len()

    result = result[["clean_review", "sentiment", "review_length"]]
    result = result.rename(columns={"clean_review": "review"})

    print(f"Удалено дубликатов: {removed_duplicates}")
    print(f"Осталось записей: {len(result)}")
    return result
