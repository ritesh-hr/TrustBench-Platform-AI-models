import os
import sys
import unittest

# Ensure repo root is on path so `import scripts.evaluate` works when tests are run
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.evaluate import context_exact_match, strip_citations


class TestEvaluateHelpers(unittest.TestCase):
    def test_strip_citations_brackets(self):
        self.assertEqual(strip_citations("1982 [ctx:doc1]"), "1982")
        self.assertEqual(strip_citations("MRR [1]"), "mrr")

    def test_context_exact_match_not_in_context(self):
        # Gold has period
        self.assertTrue(context_exact_match("Not in context.", "Not in context."))
        # Gold without period should also match normalized prediction
        self.assertTrue(context_exact_match("Not in context.", "Not in context"))
        # Should not match unrelated text
        self.assertFalse(context_exact_match("1982", "Not in context."))

    def test_context_exact_match_numeric(self):
        self.assertTrue(context_exact_match("It was founded in 1982.", "1982"))
        self.assertTrue(context_exact_match("1982", "1982"))
        self.assertFalse(context_exact_match("1983", "1982"))

    def test_context_exact_match_short_token(self):
        self.assertTrue(context_exact_match("MRR", "MRR"))
        self.assertTrue(context_exact_match("MRR (Mean Reciprocal Rank)", "MRR"))
        self.assertFalse(context_exact_match("Recall@k", "MRR"))


if __name__ == "__main__":
    unittest.main()
