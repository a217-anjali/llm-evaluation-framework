import unittest
from llm_eval_framework.contamination.detector import ContaminationDetector, ContaminationResult


class TestContaminationDetector(unittest.TestCase):
    """Test ContaminationDetector for test set contamination"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ContaminationDetector(n_gram_size=3)

    def test_exact_match_detection(self):
        """Test detection of exact training/test overlap"""
        training_text = "The quick brown fox jumps over the lazy dog"
        test_text = "The quick brown fox jumps over the lazy dog"

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertTrue(result.is_contaminated)
        self.assertEqual(result.overlap_percentage, 100.0)

    def test_no_overlap_detection(self):
        """Test detection with no overlap"""
        training_text = "Machine learning is a subset of artificial intelligence"
        test_text = "The weather is sunny and warm"

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertFalse(result.is_contaminated)
        self.assertEqual(result.overlap_percentage, 0.0)

    def test_partial_overlap_detection(self):
        """Test detection of partial overlap"""
        training_text = "The quick brown fox jumps over the lazy dog"
        test_text = "The quick brown fox jumps over a lazy dog"

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertGreater(result.overlap_percentage, 0)
        self.assertLess(result.overlap_percentage, 100)

    def test_substring_overlap_detection(self):
        """Test detection of substring overlap"""
        training_text = "The quick brown fox jumps over the lazy dog"
        test_text = "The quick brown fox"

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertGreater(result.overlap_percentage, 0)

    def test_high_overlap_threshold(self):
        """Test overlap detection with high threshold"""
        training_text = "The quick brown fox jumps over the lazy dog"
        test_text = "The quick brown fox jumps over the lazy dog"

        result = self.detector.detect_overlap(
            training_text,
            test_text,
            threshold=0.9
        )

        self.assertTrue(result.is_contaminated)

    def test_low_overlap_threshold(self):
        """Test overlap detection with low threshold"""
        training_text = "The quick brown fox jumps over the lazy dog"
        test_text = "The quick brown fox"

        result = self.detector.detect_overlap(
            training_text,
            test_text,
            threshold=0.1
        )

        self.assertTrue(result.is_contaminated)

    def test_case_insensitive_overlap(self):
        """Test case-insensitive overlap detection"""
        training_text = "The QUICK brown FOX jumps over the lazy dog"
        test_text = "the quick brown fox jumps over the lazy dog"

        result = self.detector.detect_overlap(
            training_text,
            test_text,
            case_sensitive=False
        )

        self.assertEqual(result.overlap_percentage, 100.0)

    def test_case_sensitive_overlap(self):
        """Test case-sensitive overlap detection"""
        training_text = "The QUICK brown FOX"
        test_text = "the quick brown fox"

        result = self.detector.detect_overlap(
            training_text,
            test_text,
            case_sensitive=True
        )

        self.assertEqual(result.overlap_percentage, 0.0)

    def test_ngram_extraction(self):
        """Test n-gram extraction"""
        text = "the quick brown fox"
        ngrams = self.detector.extract_ngrams(text, n=2)

        expected_ngrams = [
            "the quick",
            "quick brown",
            "brown fox"
        ]

        self.assertEqual(len(ngrams), 3)
        for ngram in expected_ngrams:
            self.assertIn(ngram.lower(), [n.lower() for n in ngrams])

    def test_different_ngram_sizes(self):
        """Test with different n-gram sizes"""
        text = "the quick brown fox"

        ngrams_2 = self.detector.extract_ngrams(text, n=2)
        ngrams_3 = self.detector.extract_ngrams(text, n=3)

        self.assertGreater(len(ngrams_2), len(ngrams_3))

    def test_empty_string_handling(self):
        """Test handling of empty strings"""
        result = self.detector.detect_overlap("", "some text")

        self.assertEqual(result.overlap_percentage, 0.0)

    def test_whitespace_normalization(self):
        """Test whitespace normalization in overlap detection"""
        training_text = "The  quick   brown   fox"
        test_text = "The quick brown fox"

        result = self.detector.detect_overlap(
            training_text,
            test_text,
            normalize_whitespace=True
        )

        self.assertEqual(result.overlap_percentage, 100.0)


class TestCanaryStringDetection(unittest.TestCase):
    """Test canary string detection for contamination"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ContaminationDetector()
        self.canary_strings = [
            "GLUE benchmark",
            "SuperGLUE dataset",
            "SQuAD v1.1",
            "MMLU test set"
        ]

    def test_exact_canary_detection(self):
        """Test exact canary string detection"""
        response = "I used the GLUE benchmark for evaluation"

        found_canaries = self.detector.detect_canary_strings(
            response,
            self.canary_strings
        )

        self.assertGreater(len(found_canaries), 0)
        self.assertIn("GLUE benchmark", found_canaries)

    def test_no_canary_detection(self):
        """Test when no canaries are present"""
        response = "This is a normal evaluation response"

        found_canaries = self.detector.detect_canary_strings(
            response,
            self.canary_strings
        )

        self.assertEqual(len(found_canaries), 0)

    def test_multiple_canary_detection(self):
        """Test detection of multiple canaries"""
        response = "I evaluated on GLUE benchmark and SuperGLUE dataset"

        found_canaries = self.detector.detect_canary_strings(
            response,
            self.canary_strings
        )

        self.assertGreaterEqual(len(found_canaries), 1)

    def test_case_insensitive_canary_detection(self):
        """Test case-insensitive canary detection"""
        response = "I used the glue benchmark for testing"

        found_canaries = self.detector.detect_canary_strings(
            response,
            self.canary_strings,
            case_sensitive=False
        )

        self.assertGreater(len(found_canaries), 0)

    def test_partial_match_canary_detection(self):
        """Test partial match in canary detection"""
        response = "The GLUE is a well-known benchmark"

        found_canaries = self.detector.detect_canary_strings(
            response,
            ["GLUE benchmark"],
            require_exact_match=False
        )

        self.assertGreater(len(found_canaries), 0)


class TestKnownContaminatedExamples(unittest.TestCase):
    """Test with known contaminated and clean examples"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ContaminationDetector(n_gram_size=3)

    def test_contaminated_example_1(self):
        """Test first known contaminated example"""
        training_data = (
            "Question: What is the capital of France? "
            "Answer: Paris is the capital of France, located on the Seine River."
        )

        test_response = (
            "The capital of France is Paris, which is located on the Seine River. "
            "It is the most populous city in France."
        )

        result = self.detector.detect_overlap(training_data, test_response)

        self.assertTrue(result.is_contaminated)
        self.assertGreater(result.overlap_percentage, 50)

    def test_contaminated_example_2(self):
        """Test second known contaminated example"""
        training_text = "Machine learning is a subset of artificial intelligence"

        test_text = (
            "Machine learning is a subset of artificial intelligence "
            "that enables systems to learn from data"
        )

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertTrue(result.is_contaminated)

    def test_clean_example_1(self):
        """Test first clean example"""
        training_data = (
            "Question: What is machine learning? "
            "Answer: Machine learning is a type of AI."
        )

        test_response = (
            "Deep learning is a specialized area focused on neural networks "
            "and is particularly effective for image and speech recognition."
        )

        result = self.detector.detect_overlap(training_data, test_response)

        self.assertLess(result.overlap_percentage, 30)

    def test_clean_example_2(self):
        """Test second clean example"""
        training_text = (
            "The Industrial Revolution occurred primarily in the 18th and 19th centuries"
        )

        test_text = (
            "Modern renewable energy technologies like solar and wind power "
            "represent significant advances in sustainable energy production."
        )

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertFalse(result.is_contaminated)

    def test_borderline_contamination(self):
        """Test borderline contamination case"""
        training_text = (
            "Python is a popular programming language for data science"
        )

        test_text = (
            "Python is widely used for data science and scientific computing. "
            "Java is another popular programming language for enterprise applications."
        )

        result = self.detector.detect_overlap(training_text, test_text)

        # Should detect some overlap but may vary by threshold
        self.assertGreater(result.overlap_percentage, 0)


class TestContaminationResult(unittest.TestCase):
    """Test ContaminationResult dataclass"""

    def test_result_creation(self):
        """Test ContaminationResult creation"""
        result = ContaminationResult(
            is_contaminated=True,
            overlap_percentage=85.5,
            matched_ngrams=["the quick", "brown fox"],
            threshold_used=0.8
        )

        self.assertTrue(result.is_contaminated)
        self.assertEqual(result.overlap_percentage, 85.5)
        self.assertEqual(len(result.matched_ngrams), 2)

    def test_result_with_no_matches(self):
        """Test ContaminationResult with no matches"""
        result = ContaminationResult(
            is_contaminated=False,
            overlap_percentage=0.0,
            matched_ngrams=[],
            threshold_used=0.8
        )

        self.assertFalse(result.is_contaminated)
        self.assertEqual(len(result.matched_ngrams), 0)

    def test_result_confidence_score(self):
        """Test contamination confidence score"""
        high_overlap = ContaminationResult(
            is_contaminated=True,
            overlap_percentage=95.0,
            matched_ngrams=["match"] * 50
        )

        low_overlap = ContaminationResult(
            is_contaminated=True,
            overlap_percentage=25.0,
            matched_ngrams=["match"] * 5
        )

        self.assertGreater(high_overlap.overlap_percentage, low_overlap.overlap_percentage)


class TestBatchContaminationDetection(unittest.TestCase):
    """Test batch contamination detection"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ContaminationDetector()

    def test_batch_detection(self):
        """Test batch contamination detection"""
        training_corpus = [
            "The quick brown fox jumps over the lazy dog",
            "Machine learning is a subset of AI",
            "Python is a programming language"
        ]

        test_samples = [
            "The quick brown fox jumps over the lazy dog",
            "Java is a programming language",
            "Deep learning is part of machine learning"
        ]

        results = self.detector.detect_batch_contamination(
            training_corpus,
            test_samples
        )

        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].is_contaminated)
        self.assertFalse(results[1].is_contaminated)

    def test_batch_detection_with_threshold(self):
        """Test batch detection with custom threshold"""
        training_corpus = ["The quick brown fox"]
        test_samples = [
            "The quick brown fox",
            "The quick brown",
            "The quick"
        ]

        results = self.detector.detect_batch_contamination(
            training_corpus,
            test_samples,
            threshold=0.5
        )

        self.assertEqual(len(results), 3)
        # Results depend on overlap percentages and threshold


class TestEdgeCases(unittest.TestCase):
    """Test edge cases in contamination detection"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = ContaminationDetector()

    def test_very_long_text(self):
        """Test with very long text"""
        long_text = "The quick brown fox " * 10000
        test_text = "The quick brown fox"

        result = self.detector.detect_overlap(long_text, test_text)

        self.assertGreater(result.overlap_percentage, 50)

    def test_special_characters(self):
        """Test with special characters"""
        training_text = "Hello @#$%^&*() World"
        test_text = "Hello @#$%^&*() World"

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertEqual(result.overlap_percentage, 100.0)

    def test_unicode_text(self):
        """Test with unicode characters"""
        training_text = "Здравствуй мир"
        test_text = "Здравствуй мир"

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertEqual(result.overlap_percentage, 100.0)

    def test_single_word(self):
        """Test with single word"""
        result = self.detector.detect_overlap("test", "test")

        self.assertEqual(result.overlap_percentage, 100.0)

    def test_numbers_only(self):
        """Test with numbers only"""
        training_text = "1234567890"
        test_text = "1234567890"

        result = self.detector.detect_overlap(training_text, test_text)

        self.assertEqual(result.overlap_percentage, 100.0)


if __name__ == '__main__':
    unittest.main()
