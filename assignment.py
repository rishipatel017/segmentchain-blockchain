"""
Assignment module for node and segment assignment.
Implements segment replica distribution across simulated nodes.
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Any
import random
from segmentation import Segment


@dataclass
class Node:
    """Represents a simulated storage node."""
    node_id: str
    segment_ids: List[str]
    is_online: bool = True
    stored_block_bytes: int = 0
    header_bytes: int = 0
    state_bytes: int = 0
    total_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            'node_id': self.node_id,
            'segment_ids': self.segment_ids,
            'is_online': self.is_online,
            'stored_block_bytes': self.stored_block_bytes,
            'header_bytes': self.header_bytes,
            'state_bytes': self.state_bytes,
            'total_bytes': self.total_bytes
        }


class AssignmentEngine:
    """Engine for assigning segment replicas to nodes."""

    def __init__(self):
        """Initialize the assignment engine."""
        self.nodes: List[Node] = []
        self.segment_replicas: Dict[str, List[str]] = {}  # segment_id -> list of node_ids

    def assign_segment_replicas(
        self,
        segments: List[Segment],
        num_nodes: int,
        replicas_per_segment: int,
        seed: int = 7
    ) -> Dict[str, Any]:
        """
        Assign segment replicas to nodes.

        Args:
            segments: List of segments to assign
            num_nodes: Number of simulated nodes
            replicas_per_segment: Number of replicas per segment
            seed: Random seed for reproducibility

        Returns:
            Dictionary with assignment matrix and validation status

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate configuration
        if num_nodes <= 0:
            raise ValueError("Number of nodes must be positive")

        if replicas_per_segment <= 0:
            raise ValueError("Replicas per segment must be positive")

        if replicas_per_segment > num_nodes:
            raise ValueError("Replicas per segment cannot exceed number of nodes")

        random.seed(seed)

        # Initialize nodes
        self.nodes = [Node(node_id=f"N{i + 1}", segment_ids=[]) for i in range(num_nodes)]
        self.segment_replicas = {}

        # Assign replicas for each segment
        for segment in segments:
            # Select random distinct nodes for this segment
            available_nodes = list(range(num_nodes))
            selected_indices = random.sample(available_nodes, replicas_per_segment)

            # Assign segment to selected nodes
            for idx in selected_indices:
                self.nodes[idx].segment_ids.append(segment.segment_id)

            # Track replicas for this segment
            self.segment_replicas[segment.segment_id] = [
                self.nodes[idx].node_id for idx in selected_indices
            ]

        # Validate assignment
        validation = self.validate_assignment(segments, replicas_per_segment)

        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'segment_replicas': self.segment_replicas,
            'validation': validation
        }

    def validate_assignment(
        self,
        segments: List[Segment],
        expected_replicas: int
    ) -> Dict[str, Any]:
        """
        Validate that each segment has the required number of distinct replicas.

        Args:
            segments: List of segments
            expected_replicas: Expected number of replicas per segment

        Returns:
            Dictionary with validation results
        """
        for segment in segments:
            replicas = self.segment_replicas.get(segment.segment_id, [])

            # Check replica count
            if len(replicas) != expected_replicas:
                return {
                    'valid': False,
                    'error': f"Segment {segment.segment_id} has {len(replicas)} replicas, expected {expected_replicas}"
                }

            # Check for duplicates
            if len(set(replicas)) != len(replicas):
                return {
                    'valid': False,
                    'error': f"Segment {segment.segment_id} has duplicate node assignments"
                }

        return {
            'valid': True,
            'error': None
        }

    def get_nodes(self) -> List[Node]:
        """Return the list of nodes."""
        return self.nodes

    def get_node_by_id(self, node_id: str) -> Node:
        """
        Get a node by its ID.

        Args:
            node_id: Node identifier (e.g., "N1", "N2")

        Returns:
            Node object

        Raises:
            ValueError: If node_id is not found
        """
        for node in self.nodes:
            if node.node_id == node_id:
                return node

        raise ValueError(f"Node {node_id} not found")

    def set_node_status(self, node_id: str, is_online: bool) -> None:
        """
        Set the online/offline status of a node.

        Args:
            node_id: Node identifier
            is_online: True if node is online, False if offline
        """
        node = self.get_node_by_id(node_id)
        node.is_online = is_online

    def reset_all_nodes(self) -> None:
        """Reset all nodes to online status."""
        for node in self.nodes:
            node.is_online = True

    def get_online_nodes(self) -> List[Node]:
        """Return list of online nodes."""
        return [node for node in self.nodes if node.is_online]

    def get_offline_nodes(self) -> List[Node]:
        """Return list of offline nodes."""
        return [node for node in self.nodes if not node.is_online]

    def get_segment_replica_count(self, segment_id: str) -> int:
        """
        Get the number of online replicas for a segment.

        Args:
            segment_id: Segment identifier

        Returns:
            Number of online replicas
        """
        if segment_id not in self.segment_replicas:
            return 0

        replica_nodes = self.segment_replicas[segment_id]
        online_count = sum(1 for node_id in replica_nodes if self.get_node_by_id(node_id).is_online)

        return online_count

    def get_assignment_matrix(self) -> List[Dict[str, Any]]:
        """
        Get the assignment matrix as a list of dictionaries.

        Returns:
            List of assignment records
        """
        matrix = []
        for node in self.nodes:
            for segment_id in node.segment_ids:
                # Find replica number
                replica_nodes = self.segment_replicas.get(segment_id, [])
                replica_number = replica_nodes.index(node.node_id) + 1

                matrix.append({
                    'node_id': node.node_id,
                    'segment_id': segment_id,
                    'replica_number': replica_number,
                    'status': 'Online' if node.is_online else 'Offline'
                })

        return matrix
