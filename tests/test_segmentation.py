"""
Unit tests for segmentation module.
"""

import unittest
from blockchain import Blockchain, Block
from segmentation import SegmentationEngine, Segment


class TestSegmentation(unittest.TestCase):
    """Test cases for SegmentationEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()
        self.blockchain.generate_chain(100, 5, seed=42)
        self.engine = SegmentationEngine()

    def test_partition_segments(self):
        """Test segment partitioning."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        self.assertEqual(len(segments), 5)

    def test_segment_ids(self):
        """Test segment ID generation."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 3)
        segment_ids = [seg.segment_id for seg in segments]
        self.assertEqual(segment_ids, ["S1", "S2", "S3"])

    def test_no_gaps(self):
        """Test that there are no gaps between segments."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        for i in range(len(segments) - 1):
            self.assertEqual(segments[i].end_height + 1, segments[i + 1].start_height)

    def test_first_segment_starts_at_zero(self):
        """Test that first segment starts at height 0."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        self.assertEqual(segments[0].start_height, 0)

    def test_last_segment_ends_at_last_block(self):
        """Test that last segment ends at last block."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        self.assertEqual(segments[-1].end_height, len(blocks) - 1)

    def test_total_blocks_accounted(self):
        """Test that all blocks are accounted for."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        total_in_segments = sum(seg.block_count for seg in segments)
        self.assertEqual(total_in_segments, len(blocks))

    def test_invalid_segment_count(self):
        """Test with invalid segment count."""
        blocks = self.blockchain.chain
        with self.assertRaises(ValueError):
            self.engine.partition_segments(blocks, 0)
        with self.assertRaises(ValueError):
            self.engine.partition_segments(blocks, 150)

    def test_empty_blockchain(self):
        """Test with empty blockchain."""
        with self.assertRaises(ValueError):
            self.engine.partition_segments([], 5)

    def test_get_segment_by_id(self):
        """Test getting segment by ID."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        segment = self.engine.get_segment_by_id("S3")
        self.assertEqual(segment.segment_id, "S3")

    def test_get_segment_by_height(self):
        """Test getting segment by block height."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        segment = self.engine.get_segment_by_height(50)
        self.assertIsNotNone(segment)
        self.assertLessEqual(segment.start_height, 50)
        self.assertGreaterEqual(segment.end_height, 50)

    def test_validate_partitioning(self):
        """Test partitioning validation."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        validation = self.engine.validate_partitioning(blocks)
        self.assertTrue(validation['valid'])
        self.assertIsNone(validation['error'])

    def test_segment_summary(self):
        """Test segment summary generation."""
        blocks = self.blockchain.chain
        segments = self.engine.partition_segments(blocks, 5)
        summary = self.engine.get_segment_summary()
        self.assertEqual(len(summary), 5)
        self.assertIn('segment_id', summary[0])
        self.assertIn('start_height', summary[0])
        self.assertIn('end_height', summary[0])
        self.assertIn('block_count', summary[0])


if __name__ == '__main__':
    unittest.main()
