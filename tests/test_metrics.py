from __future__ import annotations

import unittest

from tsrisk.metrics import char_f1, contains_match, normalized_exact_match, normalize_text


class MetricsTest(unittest.TestCase):
    def test_normalization_handles_punctuation_and_spacing(self) -> None:
        gold = '10nm，HBM-控制'
        pred = '10 nm HBM 控制'
        self.assertEqual(normalized_exact_match(pred, gold), 1.0)

    def test_chinese_char_f1_not_zero_for_paraphrase(self) -> None:
        gold = '公交车自撞隧道口'
        pred = '广州发生公交车自撞隧道口事故'
        self.assertGreater(char_f1(pred, gold), 0.5)
        self.assertEqual(contains_match(pred, gold), 1.0)


if __name__ == '__main__':
    unittest.main()
