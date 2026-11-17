
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

import monitor
from src.data_processor import clean_review, prepare_reviews


class TestIMDbProject(unittest.TestCase):

    def test_clean_review(self):
        result = clean_review("Hello <br> world  !")
        self.assertEqual(result, "Hello world !")

    def test_remove_duplicates(self):
        df = pd.DataFrame({
            "review": ["Good movie", "Good movie", "Bad movie"],
            "sentiment": ["positive", "positive", "negative"]
        })

        result = prepare_reviews(df)

        self.assertEqual(len(result), 2)

    def test_negative_alert(self):
        batch = pd.DataFrame({
            "sentiment": ["negative", "positive"]
        })

        with patch.object(monitor, "send_telegram") as telegram, \
             patch.object(monitor, "send_email") as email:

            monitor.analyze_batch(batch, 1)

            telegram.assert_called_once()
            email.assert_called_once()

    def test_no_alert(self):
        batch = pd.DataFrame({
            "sentiment": ["positive", "positive"]
        })

        with patch.object(monitor, "send_telegram") as telegram, \
             patch.object(monitor, "send_email") as email:

            monitor.analyze_batch(batch, 1)

            telegram.assert_not_called()
            email.assert_not_called()


if __name__ == "__main__":
    unittest.main()
