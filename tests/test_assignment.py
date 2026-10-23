"""
Unit tests for assignment module.
"""

import unittest
from blockchain import Blockchain
from segmentation import SegmentationEngine
from assignment import AssignmentEngine


class TestAssignment(unittest.TestCase):
    """Test cases for AssignmentEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()
        self.blockchain.generate_chain(100, 5, seed=42)
        self.segmentation_engine = SegmentationEngine()
        self.segmentation_engine.partition_segments(self.blockchain.chain, 5)
        self.assignment_engine = AssignmentEngine()

    def test_assign_segment_replicas(self):
        """Test segment replica assignment."""
        segments = self.segmentation_engine.get_segments()
        result = self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        self.assertTrue(result['validation']['valid'])
        self.assertEqual(len(result['nodes']), 10)

    def test_replica_count(self):
        """Test that each segment has correct replica count."""
        segments = self.segmentation_engine.get_segments()
        result = self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        for segment_id, replicas in result['segment_replicas'].items():
            self.assertEqual(len(replicas), 3)

    def test_distinct_replicas(self):
        """Test that replicas are assigned to distinct nodes."""
        segments = self.segmentation_engine.get_segments()
        result = self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        for segment_id, replicas in result['segment_replicas'].items():
            self.assertEqual(len(set(replicas)), len(replicas))

    def test_invalid_configuration(self):
        """Test with invalid configuration."""
        segments = self.segmentation_engine.get_segments()
        with self.assertRaises(ValueError):
            self.assignment_engine.assign_segment_replicas(segments, 0, 3)
        with self.assertRaises(ValueError):
            self.assignment_engine.assign_segment_replicas(segments, 10, 0)
        with self.assertRaises(ValueError):
            self.assignment_engine.assign_segment_replicas(segments, 5, 10)

    def test_get_node_by_id(self):
        """Test getting node by ID."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        node = self.assignment_engine.get_node_by_id("N5")
        self.assertEqual(node.node_id, "N5")

    def test_set_node_status(self):
        """Test setting node status."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        self.assignment_engine.set_node_status("N1", False)
        node = self.assignment_engine.get_node_by_id("N1")
        self.assertFalse(node.is_online)

    def test_reset_all_nodes(self):
        """Test resetting all nodes."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        self.assignment_engine.set_node_status("N1", False)
        self.assignment_engine.set_node_status("N2", False)
        self.assignment_engine.reset_all_nodes()
        for node in self.assignment_engine.get_nodes():
            self.assertTrue(node.is_online)

    def test_get_online_nodes(self):
        """Test getting online nodes."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        self.assignment_engine.set_node_status("N1", False)
        online = self.assignment_engine.get_online_nodes()
        self.assertEqual(len(online), 9)

    def test_get_offline_nodes(self):
        """Test getting offline nodes."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        self.assignment_engine.set_node_status("N1", False)
        self.assignment_engine.set_node_status("N2", False)
        offline = self.assignment_engine.get_offline_nodes()
        self.assertEqual(len(offline), 2)

    def test_get_segment_replica_count(self):
        """Test getting segment replica count."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        count = self.assignment_engine.get_segment_replica_count("S1")
        self.assertEqual(count, 3)

    def test_get_segment_replica_count_with_failures(self):
        """Test segment replica count with node failures."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        self.assignment_engine.set_node_status("N1", False)
        # Get which nodes store S1
        replicas = self.assignment_engine.segment_replicas.get("S1", [])
        if "N1" in replicas:
            count = self.assignment_engine.get_segment_replica_count("S1")
            self.assertEqual(count, 2)

    def test_get_assignment_matrix(self):
        """Test getting assignment matrix."""
        segments = self.segmentation_engine.get_segments()
        self.assignment_engine.assign_segment_replicas(segments, 10, 3, seed=42)
        matrix = self.assignment_engine.get_assignment_matrix()
        self.assertGreater(len(matrix), 0)
        self.assertIn('node_id', matrix[0])
        self.assertIn('segment_id', matrix[0])
        self.assertIn('replica_number', matrix[0])
        self.assertIn('status', matrix[0])


if __name__ == '__main__':
    unittest.main()
