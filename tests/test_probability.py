"""
Unit tests for probability module.
"""

import unittest
from probability import ProbabilityCalculator


class TestProbabilityCalculator(unittest.TestCase):
    """Test cases for ProbabilityCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ProbabilityCalculator()

    def test_segment_loss_probability(self):
        """Test segment loss probability calculation."""
        result = self.calculator.segment_loss_probability(30, 3, 3)
        self.assertIn('probability', result)
        self.assertIn('percentage', result)
        self.assertIn('total_nodes', result)
        self.assertIn('adversarial_nodes', result)
        self.assertIn('replicas_per_segment', result)
        self.assertEqual(result['total_nodes'], 30)
        self.assertEqual(result['adversarial_nodes'], 3)
        self.assertEqual(result['replicas_per_segment'], 3)

    def test_probability_formula(self):
        """Test that the formula is applied correctly."""
        # P = (3/30)^3 = (0.1)^3 = 0.001
        result = self.calculator.segment_loss_probability(30, 3, 3)
        expected = (3/30) ** 3
        self.assertAlmostEqual(result['probability'], expected, places=10)

    def test_probability_decreases_with_replicas(self):
        """Test that probability decreases as replicas increase."""
        result1 = self.calculator.segment_loss_probability(30, 3, 1)
        result2 = self.calculator.segment_loss_probability(30, 3, 3)
        result3 = self.calculator.segment_loss_probability(30, 3, 5)
        self.assertGreater(result1['probability'], result2['probability'])
        self.assertGreater(result2['probability'], result3['probability'])

    def test_invalid_inputs(self):
        """Test with invalid inputs."""
        with self.assertRaises(ValueError):
            self.calculator.segment_loss_probability(0, 3, 3)
        with self.assertRaises(ValueError):
            self.calculator.segment_loss_probability(30, -1, 3)
        with self.assertRaises(ValueError):
            self.calculator.segment_loss_probability(30, 3, 0)
        with self.assertRaises(ValueError):
            self.calculator.segment_loss_probability(30, 35, 3)
        with self.assertRaises(ValueError):
            self.calculator.segment_loss_probability(30, 3, 35)

    def test_calculate_probability_curve(self):
        """Test probability curve calculation."""
        curve = self.calculator.calculate_probability_curve(30, 3, 5)
        self.assertEqual(len(curve), 5)
        for i, result in enumerate(curve):
            self.assertEqual(result['replicas_per_segment'], i + 1)

    def test_calculate_multiple_curves(self):
        """Test multiple probability curves."""
        curves = self.calculator.calculate_multiple_curves(30, [0.1, 0.2, 0.3], 5)
        self.assertEqual(len(curves), 3)
        self.assertIn(0.1, curves)
        self.assertIn(0.2, curves)
        self.assertIn(0.3, curves)

    def test_validate_inputs_valid(self):
        """Test validation with valid inputs."""
        validation = self.calculator.validate_inputs(30, 3, 3)
        self.assertTrue(validation['valid'])
        self.assertIsNone(validation['error'])

    def test_validate_inputs_invalid(self):
        """Test validation with invalid inputs."""
        validation1 = self.calculator.validate_inputs(0, 3, 3)
        self.assertFalse(validation1['valid'])

        validation2 = self.calculator.validate_inputs(30, -1, 3)
        self.assertFalse(validation2['valid'])

        validation3 = self.calculator.validate_inputs(30, 3, 0)
        self.assertFalse(validation3['valid'])

    def test_zero_adversarial_nodes(self):
        """Test with zero adversarial nodes."""
        result = self.calculator.segment_loss_probability(30, 0, 3)
        self.assertEqual(result['probability'], 0.0)
        self.assertEqual(result['percentage'], 0.0)

    def test_get_assumptions_explanation(self):
        """Test assumptions explanation."""
        explanation = self.calculator.get_assumptions_explanation()
        self.assertIn('assumptions', explanation.lower())
        self.assertIn('theoretical', explanation.lower())


if __name__ == '__main__':
    unittest.main()
