"""
Storage metrics module for calculating and comparing storage requirements.
Implements storage estimation for full nodes and segmented nodes.
"""

from typing import List, Dict, Any
from blockchain import Block
from segmentation import Segment
from assignment import Node


class StorageMetrics:
    """Engine for calculating storage metrics and comparisons."""

    def __init__(self):
        """Initialize the storage metrics engine."""
        self.block_data_size: int = 1000  # Default bytes per block
        self.header_size: int = 160  # Default bytes per header
        self.state_size: int = 4096  # Default bytes for latest state

    def estimate_storage(
        self,
        blocks: List[Block],
        header_size: int = 160,
        state_size: int = 4096,
        block_data_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Estimate storage requirements for different scenarios.

        Args:
            blocks: List of blocks in the blockchain
            header_size: Size of each block header in bytes
            state_size: Size of latest state in bytes
            block_data_size: Size of full block data in bytes

        Returns:
            Dictionary with storage estimates
        """
        self.header_size = header_size
        self.state_size = state_size
        self.block_data_size = block_data_size

        num_blocks = len(blocks)

        # Full node storage: all block data + all headers + latest state
        full_node_storage = {
            'block_data': num_blocks * block_data_size,
            'headers': num_blocks * header_size,
            'state': state_size,
            'total': num_blocks * block_data_size + num_blocks * header_size + state_size
        }

        return {
            'full_node': full_node_storage,
            'num_blocks': num_blocks,
            'header_size': header_size,
            'state_size': state_size,
            'block_data_size': block_data_size
        }

    def calculate_segmented_storage(
        self,
        segments: List[Segment],
        nodes: List[Node],
        header_size: int = 160,
        state_size: int = 4096,
        block_data_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Calculate storage for segmented nodes.

        Args:
            segments: List of segments
            nodes: List of nodes with segment assignments
            header_size: Size of each block header in bytes
            state_size: Size of latest state in bytes
            block_data_size: Size of full block data in bytes

        Returns:
            Dictionary with segmented node storage metrics
        """
        self.header_size = header_size
        self.state_size = state_size
        self.block_data_size = block_data_size

        total_blocks = sum(seg.block_count for seg in segments)

        # Calculate storage for each node
        node_storages = []
        for node in nodes:
            # Calculate block data from assigned segments
            block_data_bytes = 0
            for segment_id in node.segment_ids:
                segment = next((s for s in segments if s.segment_id == segment_id), None)
                if segment:
                    block_data_bytes += segment.block_count * block_data_size

            # Each node stores all headers and latest state
            header_bytes = total_blocks * header_size
            state_bytes = state_size
            total_bytes = block_data_bytes + header_bytes + state_bytes

            # Update node object
            node.stored_block_bytes = block_data_bytes
            node.header_bytes = header_bytes
            node.state_bytes = state_bytes
            node.total_bytes = total_bytes

            node_storages.append({
                'node_id': node.node_id,
                'block_data': block_data_bytes,
                'headers': header_bytes,
                'state': state_bytes,
                'total': total_bytes
            })

        # Calculate statistics
        totals = [ns['total'] for ns in node_storages]
        avg_storage = sum(totals) / len(totals) if totals else 0
        min_storage = min(totals) if totals else 0
        max_storage = max(totals) if totals else 0

        return {
            'node_storages': node_storages,
            'average': avg_storage,
            'minimum': min_storage,
            'maximum': max_storage
        }

    def calculate_reduction(
        self,
        full_node_bytes: int,
        segmented_node_bytes: int
    ) -> Dict[str, Any]:
        """
        Calculate storage reduction percentage.

        Args:
            full_node_bytes: Storage required for full node
            segmented_node_bytes: Storage required for segmented node

        Returns:
            Dictionary with reduction metrics
        """
        if full_node_bytes == 0:
            return {
                'reduction_bytes': 0,
                'reduction_percentage': 0.0
            }

        reduction_bytes = full_node_bytes - segmented_node_bytes
        reduction_percentage = (reduction_bytes / full_node_bytes) * 100

        return {
            'reduction_bytes': reduction_bytes,
            'reduction_percentage': reduction_percentage
        }

    def calculate_network_storage(self, nodes: List[Node]) -> Dict[str, Any]:
        """
        Calculate total network-wide storage.

        Args:
            nodes: List of nodes with storage metrics

        Returns:
            Dictionary with network storage metrics
        """
        total_storage = sum(node.total_bytes for node in nodes)

        # Breakdown by component
        total_block_data = sum(node.stored_block_bytes for node in nodes)
        total_headers = sum(node.header_bytes for node in nodes)
        total_state = sum(node.state_bytes for node in nodes)

        return {
            'total_storage': total_storage,
            'total_block_data': total_block_data,
            'total_headers': total_headers,
            'total_state': total_state,
            'node_count': len(nodes)
        }

    def compare_storage(
        self,
        full_node_storage: Dict[str, int],
        segmented_storage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare full node vs segmented node storage.

        Args:
            full_node_storage: Full node storage metrics
            segmented_storage: Segmented node storage metrics

        Returns:
            Dictionary with comparison results
        """
        full_total = full_node_storage['total']
        avg_segmented = segmented_storage['average']

        reduction = self.calculate_reduction(full_total, avg_segmented)

        return {
            'full_node_total': full_total,
            'segmented_node_average': avg_segmented,
            'segmented_node_minimum': segmented_storage['minimum'],
            'segmented_node_maximum': segmented_storage['maximum'],
            'reduction_bytes': reduction['reduction_bytes'],
            'reduction_percentage': reduction['reduction_percentage'],
            'full_node_breakdown': full_node_storage
        }

    def format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes to human-readable string.

        Args:
            bytes_value: Number of bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} TB"
