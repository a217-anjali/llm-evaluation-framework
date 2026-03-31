import unittest
import numpy as np
from scipy import stats
from llm_eval_framework.statistics.inference import (
    bootstrap_ci,
    paired_permutation_test,
    cohens_d,
    cliffs_delta,
    holm_bonferroni_correction
)
from llm_eval_framework.statistics.selection import ParetoSelector


class TestBootstrapCI(unittest.TestCase):
    """Test bootstrap confidence interval calculation"""

    def test_bootstrap_ci_normal_distribution(self):
        """Test bootstrap CI with normally distributed data"""
        np.random.seed(42)
        data = np.random.normal(loc=100, scale=15, size=100)

        ci_lower, ci_upper = bootstrap_ci(data, confidence=0.95, n_bootstrap=1000)

        # True population mean is 100
        self.assertLess(ci_lower, 100)
        self.assertGreater(ci_upper, 100)
        self.assertLess(ci_upper - ci_lower, 20)

    def test_bootstrap_ci_different_confidence_levels(self):
        """Test bootstrap CI with different confidence levels"""
        np.random.seed(42)
        data = np.random.normal(loc=100, scale=15, size=100)

        ci_90 = bootstrap_ci(data, confidence=0.90, n_bootstrap=1000)
        ci_95 = bootstrap_ci(data, confidence=0.95, n_bootstrap=1000)
        ci_99 = bootstrap_ci(data, confidence=0.99, n_bootstrap=1000)

        # Wider confidence should have wider interval
        width_90 = ci_90[1] - ci_90[0]
        width_95 = ci_95[1] - ci_95[0]
        width_99 = ci_99[1] - ci_99[0]

        self.assertLess(width_90, width_95)
        self.assertLess(width_95, width_99)

    def test_bootstrap_ci_small_sample(self):
        """Test bootstrap CI with small sample"""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        ci_lower, ci_upper = bootstrap_ci(data, confidence=0.95, n_bootstrap=500)

        # Should contain true mean 3.0
        self.assertLess(ci_lower, 3.0)
        self.assertGreater(ci_upper, 3.0)

    def test_bootstrap_ci_single_value(self):
        """Test bootstrap CI with constant values"""
        data = np.array([5.0, 5.0, 5.0, 5.0, 5.0])

        ci_lower, ci_upper = bootstrap_ci(data, confidence=0.95, n_bootstrap=500)

        # Both should be 5.0
        self.assertAlmostEqual(ci_lower, 5.0, places=1)
        self.assertAlmostEqual(ci_upper, 5.0, places=1)

    def test_bootstrap_ci_reproducibility(self):
        """Test bootstrap CI reproducibility with seed"""
        np.random.seed(42)
        data = np.random.normal(loc=100, scale=15, size=100)

        ci1 = bootstrap_ci(data, confidence=0.95, n_bootstrap=500, random_seed=42)
        ci2 = bootstrap_ci(data, confidence=0.95, n_bootstrap=500, random_seed=42)

        self.assertAlmostEqual(ci1[0], ci2[0], places=5)
        self.assertAlmostEqual(ci1[1], ci2[1], places=5)


class TestPairedPermutationTest(unittest.TestCase):
    """Test paired permutation test for significance"""

    def test_significant_difference(self):
        """Test detection of significant difference"""
        np.random.seed(42)
        group1 = np.random.normal(loc=100, scale=10, size=50)
        group2 = np.random.normal(loc=110, scale=10, size=50)

        p_value = paired_permutation_test(group1, group2, n_permutations=1000)

        self.assertLess(p_value, 0.05)

    def test_no_significant_difference(self):
        """Test when there is no significant difference"""
        np.random.seed(42)
        group1 = np.random.normal(loc=100, scale=10, size=50)
        group2 = np.random.normal(loc=100, scale=10, size=50)

        p_value = paired_permutation_test(group1, group2, n_permutations=1000)

        self.assertGreater(p_value, 0.05)

    def test_one_tailed_test(self):
        """Test one-tailed permutation test"""
        group1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        group2 = np.array([2.0, 3.0, 4.0, 5.0, 6.0])

        p_value = paired_permutation_test(
            group1,
            group2,
            alternative="greater",
            n_permutations=1000
        )

        self.assertIsNotNone(p_value)

    def test_two_tailed_test(self):
        """Test two-tailed permutation test"""
        group1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        group2 = np.array([2.0, 3.0, 4.0, 5.0, 6.0])

        p_value = paired_permutation_test(
            group1,
            group2,
            alternative="two-sided",
            n_permutations=1000
        )

        self.assertIsNotNone(p_value)

    def test_identical_groups(self):
        """Test with identical groups"""
        group1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        group2 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        p_value = paired_permutation_test(group1, group2, n_permutations=500)

        self.assertEqual(p_value, 1.0)


class TestCohensD(unittest.TestCase):
    """Test Cohen's d effect size calculation"""

    def test_cohens_d_large_effect(self):
        """Test Cohen's d with large effect size"""
        group1 = np.array([100, 105, 110, 115, 120])
        group2 = np.array([50, 55, 60, 65, 70])

        d = cohens_d(group1, group2)

        self.assertGreater(d, 1.5)

    def test_cohens_d_small_effect(self):
        """Test Cohen's d with small effect size"""
        group1 = np.array([100, 101, 102, 103, 104])
        group2 = np.array([100.5, 101.5, 102.5, 103.5, 104.5])

        d = cohens_d(group1, group2)

        self.assertGreater(d, 0.0)
        self.assertLess(d, 0.5)

    def test_cohens_d_no_effect(self):
        """Test Cohen's d with no effect"""
        group1 = np.array([100, 101, 102, 103, 104])
        group2 = np.array([100, 101, 102, 103, 104])

        d = cohens_d(group1, group2)

        self.assertAlmostEqual(d, 0.0, places=5)

    def test_cohens_d_known_values(self):
        """Test Cohen's d with known values"""
        # Standard case: two groups with known means and pooled SD
        group1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])  # mean=3, sd=1.58
        group2 = np.array([2.0, 3.0, 4.0, 5.0, 6.0])  # mean=4, sd=1.58

        d = cohens_d(group1, group2)

        # d = (4 - 3) / pooled_sd ≈ 0.57
        self.assertGreater(d, 0.4)
        self.assertLess(d, 0.8)

    def test_cohens_d_different_sample_sizes(self):
        """Test Cohen's d with different sample sizes"""
        group1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        group2 = np.array([6.0, 7.0, 8.0])

        d = cohens_d(group1, group2)

        self.assertGreater(d, 1.0)


class TestCliffssDelta(unittest.TestCase):
    """Test Cliff's delta non-parametric effect size"""

    def test_cliffs_delta_large_effect(self):
        """Test Cliff's delta with large effect size"""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([10, 11, 12, 13, 14])

        delta = cliffs_delta(group1, group2)

        self.assertEqual(delta, 1.0)

    def test_cliffs_delta_small_effect(self):
        """Test Cliff's delta with small effect size"""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([4, 5, 6, 7, 8])

        delta = cliffs_delta(group1, group2)

        self.assertGreater(delta, 0.0)
        self.assertLess(delta, 1.0)

    def test_cliffs_delta_no_effect(self):
        """Test Cliff's delta with no effect"""
        group1 = np.array([1, 2, 3, 4, 5])
        group2 = np.array([1, 2, 3, 4, 5])

        delta = cliffs_delta(group1, group2)

        self.assertEqual(delta, 0.0)

    def test_cliffs_delta_negative_effect(self):
        """Test Cliff's delta with negative effect"""
        group1 = np.array([10, 11, 12, 13, 14])
        group2 = np.array([1, 2, 3, 4, 5])

        delta = cliffs_delta(group1, group2)

        self.assertEqual(delta, -1.0)

    def test_cliffs_delta_bounds(self):
        """Test Cliff's delta bounds [-1, 1]"""
        group1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        group2 = np.array([5, 6, 7, 8, 9, 10, 11, 12, 13, 14])

        delta = cliffs_delta(group1, group2)

        self.assertGreaterEqual(delta, -1.0)
        self.assertLessEqual(delta, 1.0)


class TestHolmBonferroniCorrection(unittest.TestCase):
    """Test Holm-Bonferroni multiple comparison correction"""

    def test_single_comparison(self):
        """Test with single comparison"""
        p_values = [0.05]

        corrected = holm_bonferroni_correction(p_values)

        self.assertEqual(corrected[0], 0.05)

    def test_multiple_comparisons(self):
        """Test with multiple comparisons"""
        p_values = [0.01, 0.02, 0.03, 0.04, 0.05]

        corrected = holm_bonferroni_correction(p_values)

        # Corrected p-values should be adjusted
        self.assertEqual(len(corrected), 5)
        # First value (smallest) should be multiplied by n
        self.assertEqual(corrected[0], 0.01 * 5)

    def test_holm_correction_ordering(self):
        """Test that Holm correction maintains ordering"""
        p_values = [0.001, 0.01, 0.02, 0.03, 0.5]

        corrected = holm_bonferroni_correction(p_values)

        # Corrected values should maintain ordering (non-decreasing)
        for i in range(len(corrected) - 1):
            self.assertLessEqual(corrected[i], corrected[i+1])

    def test_holm_correction_bounds(self):
        """Test that corrected p-values don't exceed 1"""
        p_values = [0.1, 0.2, 0.3, 0.4, 0.5]

        corrected = holm_bonferroni_correction(p_values)

        for p in corrected:
            self.assertLessEqual(p, 1.0)

    def test_significant_comparisons(self):
        """Test identification of significant comparisons after correction"""
        p_values = [0.001, 0.01, 0.05, 0.1, 0.5]

        corrected = holm_bonferroni_correction(p_values, alpha=0.05)

        # First two should be significant after Holm correction
        self.assertLess(corrected[0], 0.05)
        self.assertLess(corrected[1], 0.05)


class TestParetoSelector(unittest.TestCase):
    """Test Pareto selector for multi-objective optimization"""

    def setUp(self):
        """Set up test fixtures"""
        self.selector = ParetoSelector()

    def test_pareto_front_2d(self):
        """Test Pareto front selection in 2D"""
        objectives = [
            (10, 5),    # Pareto optimal
            (15, 3),    # Pareto optimal
            (8, 10),    # Pareto optimal
            (12, 6),    # Dominated by (10,5) and (15,3)
            (20, 1)     # Pareto optimal
        ]

        pareto = self.selector.select(objectives, maximize=[True, False])

        self.assertEqual(len(pareto), 4)

    def test_pareto_front_identical_points(self):
        """Test Pareto front with identical points"""
        objectives = [
            (10, 5),
            (10, 5),
            (15, 3)
        ]

        pareto = self.selector.select(objectives, maximize=[True, False])

        # Should handle duplicates
        self.assertGreaterEqual(len(pareto), 1)

    def test_pareto_single_objective(self):
        """Test Pareto with single objective"""
        objectives = [(1,), (5,), (3,)]

        pareto = self.selector.select(objectives, maximize=[True])

        self.assertEqual(len(pareto), 1)
        self.assertEqual(pareto[0], 1)  # Index of maximum

    def test_pareto_maximize_minimize_mix(self):
        """Test Pareto with mixed maximize/minimize"""
        objectives = [
            (100, 5),   # High accuracy, low latency (good)
            (95, 2),    # Lower accuracy, very low latency
            (90, 10),   # Lower accuracy, high latency
            (98, 8)     # Good accuracy, moderate latency
        ]

        pareto = self.selector.select(
            objectives,
            maximize=[True, False]  # Maximize accuracy, minimize latency
        )

        # (100, 5) should be Pareto optimal
        self.assertIn(0, pareto)

    def test_pareto_3d(self):
        """Test Pareto front in 3D space"""
        objectives = [
            (10, 20, 30),
            (15, 15, 25),
            (8, 22, 35),
            (12, 18, 28),
            (20, 10, 20)
        ]

        pareto = self.selector.select(
            objectives,
            maximize=[True, True, False]
        )

        self.assertGreater(len(pareto), 0)

    def test_pareto_all_dominated(self):
        """Test when all points are dominated by one"""
        objectives = [
            (5, 5),
            (10, 10),
            (8, 8)
        ]

        pareto = self.selector.select(objectives, maximize=[True, True])

        # Only (10, 10) is Pareto optimal
        self.assertEqual(len(pareto), 1)
        self.assertEqual(pareto[0], 1)

    def test_pareto_metrics_ranking(self):
        """Test Pareto selection for ranking evaluation metrics"""
        # Objectives: (precision, recall, f1)
        model_scores = [
            (0.95, 0.85, 0.90),  # Model 1: High precision
            (0.90, 0.92, 0.91),  # Model 2: Balanced
            (0.88, 0.95, 0.91),  # Model 3: High recall
            (0.80, 0.80, 0.80)   # Model 4: Mediocre
        ]

        pareto = self.selector.select(
            model_scores,
            maximize=[True, True, True]
        )

        # Multiple models should be on Pareto front
        self.assertGreater(len(pareto), 1)
        # Model 4 should not be Pareto optimal
        self.assertNotIn(3, pareto)


class TestStatisticalEdgeCases(unittest.TestCase):
    """Test edge cases in statistical functions"""

    def test_bootstrap_ci_single_observation(self):
        """Test bootstrap CI with single observation"""
        data = np.array([5.0])

        ci_lower, ci_upper = bootstrap_ci(data, confidence=0.95, n_bootstrap=100)

        self.assertIsNotNone(ci_lower)
        self.assertIsNotNone(ci_upper)

    def test_cohens_d_zero_variance(self):
        """Test Cohen's d with zero variance in one group"""
        group1 = np.array([5.0, 5.0, 5.0])
        group2 = np.array([3.0, 4.0, 5.0, 6.0])

        d = cohens_d(group1, group2)

        self.assertGreater(d, 0.0)

    def test_cliffs_delta_single_element(self):
        """Test Cliff's delta with single element groups"""
        group1 = np.array([5.0])
        group2 = np.array([10.0])

        delta = cliffs_delta(group1, group2)

        self.assertEqual(delta, 1.0)

    def test_holm_correction_empty_list(self):
        """Test Holm correction with empty list"""
        p_values = []

        corrected = holm_bonferroni_correction(p_values)

        self.assertEqual(len(corrected), 0)


if __name__ == '__main__':
    unittest.main()
