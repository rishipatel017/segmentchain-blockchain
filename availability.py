"""
Availability module for simulating node failures.
Implements node failure simulation and segment availability calculations.
"""

from typing import List, Dict, Any, Set
import random
from assignment import AssignmentEngine


class AvailabilitySimulator:
    """Simulator for node failures and segment availability."""

    def __init__(self, assignment_engine: AssignmentEngine):
        """
        Initialize the availability simulator.

        Args:
            assignment_engine: AssignmentEngine with node and segment assignments
        """
        self.assignment_engine = assignment_engine
        self.failed_nodes: Set[str] = set()

    def simulate_node_failures(
        self,
        failed_node_ids: List[str] = None,
        failure_percentage: float = 0.0,
        seed: int = 7
    ) -> Dict[str, Any]:
        """
        Simulate node failures and calculate segment availability.

        Args:
            failed_node_ids: Specific node IDs to fail (optional)
            failure_percentage: Percentage of nodes to fail randomly (optional)
            seed: Random seed for reproducibility

        Returns:
            Dictionary with availability metrics
        """
        # Reset to initial state
        self.assignment_engine.reset_all_nodes()
        self.failed_nodes.clear()

        nodes = self.assignment_engine.get_nodes()
        total_nodes = len(nodes)

        if failed_node_ids is not None:
            # Fail specific nodes
            for node_id in failed_node_ids:
                try:
                    self.assignment_engine.set_node_status(node_id, False)
                    self.failed_nodes.add(node_id)
                except ValueError:
                    pass  # Node not found, skip
        elif failure_percentage > 0:
            # Fail random percentage of nodes
            random.seed(seed)
            num_failures = int(total_nodes * failure_percentage / 100)
            if num_failures > 0:
                nodes_to_fail = random.sample([n.node_id for n in nodes], num_failures)
                for node_id in nodes_to_fail:
                    self.assignment_engine.set_node_status(node_id, False)
                    self.failed_nodes.add(node_id)

        # Calculate segment availability
        segment_replicas = self.assignment_engine.segment_replicas
        surviving_replicas = {}
        lost_segments = []

        for segment_id, replica_nodes in segment_replicas.items():
            surviving_count = self.assignment_engine.get_segment_replica_count(segment_id)
            surviving_replicas[segment_id] = surviving_count

            if surviving_count == 0:
                lost_segments.append(segment_id)

        online_nodes = self.assignment_engine.get_online_nodes()
        offline_nodes = self.assignment_engine.get_offline_nodes()

        total_segments = len(segment_replicas)
        available_segments = total_segments - len(lost_segments)
        availability_percentage = (available_segments / total_segments * 100) if total_segments > 0 else 0

        return {
            'total_nodes': total_nodes,
            'online_nodes': len(online_nodes),
            'offline_nodes': len(offline_nodes),
            'failed_node_ids': list(self.failed_nodes),
            'surviving_replicas': surviving_replicas,
            'total_segments': total_segments,
            'available_segments': available_segments,
            'lost_segments': lost_segments,
            'availability_percentage': availability_percentage
        }

    def fail_random_nodes(
        self,
        num_failures: int,
        seed: int = 7
    ) -> Dict[str, Any]:
        """
        Fail a specific number of random nodes.

        Args:
            num_failures: Number of nodes to fail
            seed: Random seed for reproducibility

        Returns:
            Dictionary with availability metrics
        """
        nodes = self.assignment_engine.get_nodes()
        if num_failures > len(nodes):
            num_failures = len(nodes)

        random.seed(seed)
        nodes_to_fail = random.sample([n.node_id for n in nodes], num_failures)

        return self.simulate_node_failures(failed_node_ids=nodes_to_fail, seed=seed)

    def restore_node(self, node_id: str) -> None:
        """
        Restore a failed node to online status.

        Args:
            node_id: Node identifier to restore
        """
        self.assignment_engine.set_node_status(node_id, True)
        self.failed_nodes.discard(node_id)

    def restore_all_nodes(self) -> None:
        """Restore all failed nodes to online status."""
        self.assignment_engine.reset_all_nodes()
        self.failed_nodes.clear()

    def get_segment_status(self, segment_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific segment.

        Args:
            segment_id: Segment identifier

        Returns:
            Dictionary with segment status
        """
        surviving_replicas = self.assignment_engine.get_segment_replica_count(segment_id)
        is_available = surviving_replicas > 0

        return {
            'segment_id': segment_id,
            'surviving_replicas': surviving_replicas,
            'is_available': is_available
        }

    def get_all_segment_status(self) -> List[Dict[str, Any]]:
        """
        Get the status of all segments.

        Returns:
            List of segment status dictionaries
        """
        segment_replicas = self.assignment_engine.segment_replicas
        return [
            self.get_segment_status(segment_id)
            for segment_id in segment_replicas.keys()
        ]

    def get_critical_segments(self) -> List[str]:
        """
        Get segments with only one surviving replica.

        Returns:
            List of segment IDs with single replica
        """
        segment_replicas = self.assignment_engine.segment_replicas
        critical = []

        for segment_id in segment_replicas.keys():
            surviving = self.assignment_engine.get_segment_replica_count(segment_id)
            if surviving == 1:
                critical.append(segment_id)

        return critical
