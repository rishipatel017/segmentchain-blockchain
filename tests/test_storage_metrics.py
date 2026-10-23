"""
Unit tests for storage metrics module.
"""

import unittest
from blockchain import Blockchain
from segmentation import SegmentationEngine
from assignment import AssignmentEngine
from storage_metrics import StorageMetrics


class TestStorageMetrics(unittest.TestCase):
    """Test cases for StorageMetrics class."""

    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()
        self.blockchain.generate_chain(100, 5, seed=42)
        self.segmentation_engine = SegmentationEngine()
        self.segmentation_engine.partition_segments(self.blockchain.chain, 5)
        self.assignment_engine = AssignmentEngine()
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        self.storage_metrics = StorageMetrics()

    def test_estimate_storage(self):
        """Test storage estimation."""
        blocks = self.blockchain.chain
        result = self.storage_metrics.estimate_storage(blocks, 160, 4096, 1000)
        self.assertIn('full_node', result)
        self.assertIn('num_blocks', result)
        self.assertEqual(result['num_blocks'], 100)

    def test_full_node_storage_calculation(self):
        """Test full node storage calculation."""
        blocks = self.blockchain.chain
        result = self.storage_metrics.estimate_storage(blocks, 160, 4096, 1000)
        full_node = result['full_node']
        expected_total = 100 * 1000 + 100 * 160 + 4096
        self.assertEqual(full_node['total'], expected_total)

    def test_calculate_segmented_storage(self):
        """Test segmented storage calculation."""
        segments = self.segmentation_engine.get_segments()
        nodes = self.assignment_engine.get_nodes()
        result = self.storage_metrics.calculate_segmented_storage(
            segments, nodes, 160, 4096, 1000
        )
        self.assertIn('node_storages', result)
        self.assertIn('average', result)
        self.assertIn('minimum', result)
        self.assertIn('maximum', result)
        self.assertEqual(len(result['node_storages']), 10)

    def test_calculate_reduction(self):
        """Test storage reduction calculation."""
        reduction = self.storage_metrics.calculate_reduction(10000, 6000)
        self.assertEqual(reduction['reduction_bytes'], 4000)
        self.assertEqual(reduction['reduction_percentage'], 40.0)

    def test_calculate_reduction_with_zero(self):
        """Test reduction calculation with zero full node storage."""
        reduction = self.storage_metrics.calculate_reduction(0, 0)
        self.assertEqual(reduction['reduction_bytes'], 0)
        self.assertEqual(reduction['reduction_percentage'], 0.0)

    def test_calculate_network_storage(self):
        """Test network storage calculation."""
        segments = self.segmentation_engine.get_segments()
        nodes = self.assignment_engine.get_nodes()
        self.storage_metrics.calculate_segmented_storage(
            segments, nodes, 160, 4096, 1000
        )
        result = self.storage_metrics.calculate_network_storage(nodes)
        self.assertIn('total_storage', result)
        self.assertIn('node_count', result)
        self.assertEqual(result['node_count'], 10)

    def test_compare_storage(self):
        """Test storage comparison."""
        blocks = self.blockchain.chain
        segments = self.segmentation_engine.get_segments()
        nodes = self.assignment_engine.get_nodes()

        full_storage = self.storage_metrics.estimate_storage(blocks, 160, 4096, 1000)
        segmented_storage = self.storage_metrics.calculate_segmented_storage(
            segments, nodes, 160, 4096, 1000
        )

        comparison = self.storage_metrics.compare_storage(
            full_storage['full_node'],
            segmented_storage
        )

        self.assertIn('full_node_total', comparison)
        self.assertIn('segmented_node_average', comparison)
        self.assertIn('reduction_percentage', comparison)

    def test_format_bytes(self):
        """Test byte formatting."""
        self.assertEqual(self.storage_metrics.format_bytes(500), "500.00 B")
        self.assertEqual(self.storage_metrics.format_bytes(1500), "1.46 KB")
        self.assertEqual(self.storage_metrics.format_bytes(1500000), "1.43 MB")
        self.assertEqual(self.storage_metrics.format_bytes(1500000000), "1.40 GB")


if __name__ == '__main__':
    unittest.main()
