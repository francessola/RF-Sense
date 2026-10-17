import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evaluation import calculate_precision, calculate_recall, calculate_f1_score


class TestEvaluation(unittest.TestCase):

    def test_precision(self):
        result = calculate_precision(18,6)

        self.assertAlmostEqual(result, 0.75)

    def test_recall(self):
        result = calculate_recall(32,8)

        self.assertAlmostEqual(result, 0.80)

    def test_f1_score(self):
        result = calculate_f1_score(18,6,12)

        self.assertAlmostEqual(result, 0.6666666666666)

    def test_precision_zero_predictions(self):
        result = calculate_precision(0,0)

        self.assertEqual(result, 0.0)

    def test_recall_zero_actual_positives(self):
        result = calculate_recall(0,0)

        self.assertEqual(result, 0.0)

    def test_f1_score_zero(self):
        result = calculate_f1_score(0,0,0)

        self.assertEqual(result, 0.0)


if __name__ == "__main__":
    unittest.main()