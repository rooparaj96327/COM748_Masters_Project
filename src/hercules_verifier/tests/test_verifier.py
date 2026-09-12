import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import hercules_verifier as verifier  # noqa: E402


class CitationTests(unittest.TestCase):
    def test_neutral_citation(self):
        self.assertEqual(
            verifier.classify_citation("English v Emery [2002] EWCA Civ 605", "case_law"),
            "neutral",
        )

    def test_report_citation(self):
        self.assertEqual(verifier.classify_citation("[2000] 1 WLR 377", "case_law"), "report")

    def test_legislation(self):
        self.assertEqual(verifier.classify_citation("Human Rights Act 1998", "legislation"), "legislation")

    def test_exact_neutral_signature_matches(self):
        score = verifier.authority_match_score(
            "English v Emery [2002] EWCA Civ 605",
            "English v Emery Reimbold & Strick Ltd [2002] EWCA Civ 605",
        )
        self.assertEqual(score, 1.0)


class EvidenceTests(unittest.TestCase):
    def test_similarity_prefers_relevant_passage(self):
        claim = "The authority owed no duty of care for the road hazard."
        score, passage = verifier.passage_similarity(
            claim,
            [
                "This passage concerns tax procedure and statutory appeals.",
                "The authority owed no duty of care in relation to the road hazard.",
            ],
        )
        self.assertGreater(score, 0.5)
        self.assertIn("road hazard", passage)

    def test_missing_holding_source_is_unclear(self):
        result = verifier.predict_holding(
            {"generated_principle": "A judgment must provide reasons."},
            "neutral",
            None,
            None,
            verifier.Thresholds(),
        )
        self.assertEqual(result[0], "unclear")


class MetricTests(unittest.TestCase):
    def test_degenerate_prediction_has_zero_kappa(self):
        rows = [
            {"pred": "no", "truth": "no"},
            {"pred": "no", "truth": "partial"},
            {"pred": "no", "truth": "yes"},
        ]
        metrics = verifier.classification_metrics(rows, "pred", "truth")
        self.assertAlmostEqual(metrics["cohens_kappa"], 0.0)
        self.assertAlmostEqual(metrics["balanced_accuracy"], 1 / 3)


if __name__ == "__main__":
    unittest.main()