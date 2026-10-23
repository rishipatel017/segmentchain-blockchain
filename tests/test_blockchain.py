"""
Unit tests for blockchain module.
"""

import unittest
from blockchain import Blockchain, Block, Transaction


class TestBlockchain(unittest.TestCase):
    """Test cases for Blockchain class."""

    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()

    def test_generate_chain(self):
        """Test blockchain generation."""
        chain = self.blockchain.generate_chain(10, 5, seed=42)
        self.assertEqual(len(chain), 10)
        self.assertEqual(chain[0].index, 0)
        self.assertEqual(chain[9].index, 9)

    def test_genesis_block(self):
        """Test genesis block creation."""
        chain = self.blockchain.generate_chain(5, 3, seed=42)
        genesis = chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0" * 64)

    def test_block_linking(self):
        """Test that blocks are properly linked."""
        chain = self.blockchain.generate_chain(5, 3, seed=42)
        for i in range(1, len(chain)):
            self.assertEqual(chain[i].previous_hash, chain[i-1].block_hash)

    def test_hash_transactions(self):
        """Test transaction hashing."""
        transactions = [
            Transaction("A", "B", 10.0, "tx1"),
            Transaction("B", "C", 5.0, "tx2")
        ]
        hash1 = Blockchain.hash_transactions(transactions)
        hash2 = Blockchain.hash_transactions(transactions)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA-256 produces 64 hex chars

    def test_calculate_block_hash(self):
        """Test block hash calculation."""
        hash1 = Blockchain.calculate_block_hash(0, 1234567890.0, "abc", "def")
        hash2 = Blockchain.calculate_block_hash(0, 1234567890.0, "abc", "def")
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_verify_valid_chain(self):
        """Test verification of a valid chain."""
        chain = self.blockchain.generate_chain(10, 5, seed=42)
        result = self.blockchain.verify_chain(chain)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])

    def test_verify_tampered_transaction(self):
        """Test detection of tampered transaction."""
        chain = self.blockchain.generate_chain(5, 3, seed=42)
        # Tamper with a transaction
        chain[2].transactions[0].amount = 99999.0
        result = self.blockchain.verify_chain(chain)
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])

    def test_verify_broken_link(self):
        """Test detection of broken previous hash link."""
        chain = self.blockchain.generate_chain(5, 3, seed=42)
        # Break the link
        chain[2].previous_hash = "0" * 64
        result = self.blockchain.verify_chain(chain)
        self.assertFalse(result['valid'])

    def test_get_block_count(self):
        """Test getting block count."""
        self.blockchain.generate_chain(15, 5, seed=42)
        self.assertEqual(self.blockchain.get_block_count(), 15)

    def test_get_transaction_count(self):
        """Test getting total transaction count."""
        self.blockchain.generate_chain(10, 5, seed=42)
        self.assertEqual(self.blockchain.get_transaction_count(), 50)

    def test_get_block_hashes(self):
        """Test getting block hashes."""
        chain = self.blockchain.generate_chain(5, 3, seed=42)
        hashes = self.blockchain.get_block_hashes()
        self.assertEqual(len(hashes), 5)
        self.assertEqual(len(hashes[0]), 64)


if __name__ == '__main__':
    unittest.main()
