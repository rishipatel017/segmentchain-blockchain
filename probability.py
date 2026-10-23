"""
Probability module for theoretical segment-loss probability.
Implements the formula from the research paper: P = (AD/n)^m
"""

from typing import List, Dict, Any


class ProbabilityCalculator:
    """Calculator for theoretical segment-loss probability."""

    def __init__(self):
        """Initialize the probability calculator."""
        pass

    def segment_loss_probability(
        self,
        total_nodes: int,
        adversarial_nodes: int,
        replicas_per_segment: int
    ) -> Dict[str, Any]:
        """
        Calculate the theoretical segment-loss probability.

        Formula from the paper: P = (AD/n)^m
        Where:
        - P: probability of losing all copies of a segment
        - A: assumed maximum number of adversarial nodes
        - D: total number of nodes (n in the formula)
        - m: number of nodes storing each segment (replicas)

        Args:
            total_nodes: Total number of nodes (n)
            adversarial_nodes: Assumed maximum adversarial nodes (A)
            replicas_per_segment: Number of nodes storing each segment (m)

        Returns:
            Dictionary with probability and validation

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if total_nodes <= 0:
            raise ValueError("Total nodes must be positive")

        if adversarial_nodes < 0:
            raise ValueError("Adversarial nodes cannot be negative")

        if replicas_per_segment <= 0:
            raise ValueError("Replicas per segment must be positive")

        if adversarial_nodes > total_nodes:
            raise ValueError("Adversarial nodes cannot exceed total nodes")

        if replicas_per_segment > total_nodes:
            raise ValueError("Replicas per segment cannot exceed total nodes")

        # Calculate probability using the formula: P = (A/n)^m
        # Note: The paper uses D for total nodes, which is 'n' in the formula
        adversarial_fraction = adversarial_nodes / total_nodes

        # P = (A/n)^m
        probability = adversarial_fraction ** replicas_per_segment

        return {
            'probability': probability,
            'percentage': probability * 100,
            'adversarial_fraction': adversarial_fraction,
            'total_nodes': total_nodes,
            'adversarial_nodes': adversarial_nodes,
            'replicas_per_segment': replicas_per_segment,
            'formula': f"P = ({adversarial_nodes}/{total_nodes})^{replicas_per_segment}"
        }

    def calculate_probability_curve(
        self,
        total_nodes: int,
        adversarial_nodes: int,
        max_replicas: int
    ) -> List[Dict[str, Any]]:
        """
        Calculate probability for a range of replica counts.

        Args:
            total_nodes: Total number of nodes
            adversarial_nodes: Assumed maximum adversarial nodes
            max_replicas: Maximum number of replicas to calculate for

        Returns:
            List of probability results for each replica count
        """
        results = []

        for replicas in range(1, max_replicas + 1):
            try:
                result = self.segment_loss_probability(
                    total_nodes,
                    adversarial_nodes,
                    replicas
                )
                results.append(result)
            except ValueError:
                # Skip invalid configurations
                continue

        return results

    def calculate_multiple_curves(
        self,
        total_nodes: int,
        adversarial_percentages: List[float],
        max_replicas: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calculate probability curves for multiple adversarial percentages.

        Args:
            total_nodes: Total number of nodes
            adversarial_percentages: List of adversarial percentages (e.g., [0.1, 0.2, 0.3])
            max_replicas: Maximum number of replicas to calculate for

        Returns:
            Dictionary mapping percentages to probability curves
        """
        curves = {}

        for percentage in adversarial_percentages:
            adversarial_nodes = int(total_nodes * percentage)
            curve = self.calculate_probability_curve(
                total_nodes,
                adversarial_nodes,
                max_replicas
            )
            curves[percentage] = curve

        return curves

    def get_assumptions_explanation(self) -> str:
        """
        Get an explanation of the assumptions in the probability model.

        Returns:
            String explaining the model's assumptions
        """
        return """
Theoretical Segment-Loss Probability Model

This calculator implements the formula from the research paper:
P = (A/n)^m

Assumptions:
1. Adversarial nodes act in coordination to target specific segments
2. The maximum number of adversarial nodes (A) is known or assumed
3. All adversarial nodes are simultaneously available to attack
4. Replicas are distributed uniformly at random
5. The probability represents the worst-case scenario for segment loss

Limitations:
- This is a theoretical model, not a prediction of real-world failures
- It assumes adversarial behavior, not random node failures
- Real networks may have different failure patterns
- The model does not account for geographic distribution or network topology

This calculator is for educational purposes to demonstrate how increasing
replica count reduces the theoretical probability of segment loss under
the paper's assumptions.
"""

    def validate_inputs(
        self,
        total_nodes: int,
        adversarial_nodes: int,
        replicas_per_segment: int
    ) -> Dict[str, Any]:
        """
        Validate probability calculator inputs.

        Args:
            total_nodes: Total number of nodes
            adversarial_nodes: Assumed maximum adversarial nodes
            replicas_per_segment: Number of nodes storing each segment

        Returns:
            Dictionary with validation status and error message
        """
        if total_nodes <= 0:
            return {
                'valid': False,
                'error': 'Total nodes must be positive'
            }

        if adversarial_nodes < 0:
            return {
                'valid': False,
                'error': 'Adversarial nodes cannot be negative'
            }

        if replicas_per_segment <= 0:
            return {
                'valid': False,
                'error': 'Replicas per segment must be positive'
            }

        if adversarial_nodes > total_nodes:
            return {
                'valid': False,
                'error': 'Adversarial nodes cannot exceed total nodes'
            }

        if replicas_per_segment > total_nodes:
            return {
                'valid': False,
                'error': 'Replicas per segment cannot exceed total nodes'
            }

        return {
            'valid': True,
            'error': None
        }
