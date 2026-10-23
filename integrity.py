"""
Integrity module for blockchain verification and tampering detection.
Implements tampering experiments on disposable copies of the blockchain.
"""

from typing import List, Dict, Any
import copy
from blockchain import Block, Transaction, Blockchain


class IntegrityChecker:
    """Checker for blockchain integrity and tampering detection."""

    def __init__(self, blockchain: Blockchain):
        """
        Initialize the integrity checker.

        Args:
            blockchain: Blockchain instance to check
        """
        self.blockchain = blockchain
        self.original_chain = None

    def save_original(self) -> None:
        """Save a copy of the original chain for restoration."""
        self.original_chain = copy.deepcopy(self.blockchain.chain)

    def restore_original(self) -> None:
        """Restore the original chain from the saved copy."""
        if self.original_chain is not None:
            self.blockchain.chain = copy.deepcopy(self.original_chain)

    def tamper_copy(
        self,
        block_index: int,
        transaction_index: int = 0,
        new_amount: float = None
    ) -> Dict[str, Any]:
        """
        Create a tampered copy of the blockchain for demonstration.

        Args:
            block_index: Index of block to tamper with
            transaction_index: Index of transaction within the block
            new_amount: New amount to set (random if not provided)

        Returns:
            Dictionary with tampered chain and verification results
        """
        # Save original if not already saved
        if self.original_chain is None:
            self.save_original()

        # Create a disposable copy
        tampered_chain = copy.deepcopy(self.blockchain.chain)

        # Apply tampering
        if block_index < len(tampered_chain):
            block = tampered_chain[block_index]

            if transaction_index < len(block.transactions):
                import random
                if new_amount is None:
                    new_amount = random.uniform(1000, 10000)

                # Modify transaction amount
                original_amount = block.transactions[transaction_index].amount
                block.transactions[transaction_index].amount = new_amount

                # Recalculate hashes
                block.data_hash = self.blockchain.hash_transactions(block.transactions)
                block.block_hash = self.blockchain.calculate_block_hash(
                    block.index,
                    block.timestamp,
                    block.data_hash,
                    block.previous_hash
                )

                # Verify the tampered chain
                temp_blockchain = Blockchain()
                temp_blockchain.chain = tampered_chain
                verification = temp_blockchain.verify_chain()

                return {
                    'tampered_chain': tampered_chain,
                    'verification': verification,
                    'block_index': block_index,
                    'transaction_index': transaction_index,
                    'original_amount': original_amount,
                    'tampered_amount': new_amount,
                    'tamper_type': 'transaction_amount'
                }

        return {
            'error': 'Invalid block or transaction index'
        }

    def tamper_previous_hash(
        self,
        block_index: int,
        new_previous_hash: str = None
    ) -> Dict[str, Any]:
        """
        Tamper with the previous hash link of a block.

        Args:
            block_index: Index of block to tamper with
            new_previous_hash: New previous hash to set (random if not provided)

        Returns:
            Dictionary with tampered chain and verification results
        """
        # Save original if not already saved
        if self.original_chain is None:
            self.save_original()

        # Create a disposable copy
        tampered_chain = copy.deepcopy(self.blockchain.chain)

        # Apply tampering
        if block_index < len(tampered_chain) and block_index > 0:
            block = tampered_chain[block_index]

            if new_previous_hash is None:
                import random
                import hashlib
                new_previous_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()

            # Modify previous hash
            original_previous_hash = block.previous_hash
            block.previous_hash = new_previous_hash

            # Recalculate block hash
            block.block_hash = self.blockchain.calculate_block_hash(
                block.index,
                block.timestamp,
                block.data_hash,
                block.previous_hash
            )

            # Verify the tampered chain
            temp_blockchain = Blockchain()
            temp_blockchain.chain = tampered_chain
            verification = temp_blockchain.verify_chain()

            return {
                'tampered_chain': tampered_chain,
                'verification': verification,
                'block_index': block_index,
                'original_previous_hash': original_previous_hash,
                'tampered_previous_hash': new_previous_hash,
                'tamper_type': 'previous_hash'
            }

        return {
            'error': 'Invalid block index (must be > 0)'
        }

    def verify_chain(self) -> Dict[str, Any]:
        """
        Verify the current blockchain integrity.

        Returns:
            Dictionary with verification results
        """
        return self.blockchain.verify_chain()

    def get_block_details(self, block_index: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific block.

        Args:
            block_index: Index of block to inspect

        Returns:
            Dictionary with block details
        """
        if block_index < len(self.blockchain.chain):
            block = self.blockchain.chain[block_index]
            return {
                'index': block.index,
                'timestamp': block.timestamp,
                'transaction_count': len(block.transactions),
                'previous_hash': block.previous_hash,
                'data_hash': block.data_hash,
                'block_hash': block.block_hash,
                'transactions': [tx.to_dict() for tx in block.transactions]
            }

        return {
            'error': 'Block index out of range'
        }

    def compare_hashes(
        self,
        block_index: int,
        expected_data_hash: str,
        expected_block_hash: str
    ) -> Dict[str, Any]:
        """
        Compare current block hashes with expected values.

        Args:
            block_index: Index of block to compare
            expected_data_hash: Expected data hash
            expected_block_hash: Expected block hash

        Returns:
            Dictionary with comparison results
        """
        if block_index < len(self.blockchain.chain):
            block = self.blockchain.chain[block_index]

            return {
                'block_index': block_index,
                'data_hash_match': block.data_hash == expected_data_hash,
                'current_data_hash': block.data_hash,
                'expected_data_hash': expected_data_hash,
                'block_hash_match': block.block_hash == expected_block_hash,
                'current_block_hash': block.block_hash,
                'expected_block_hash': expected_block_hash
            }

        return {
            'error': 'Block index out of range'
        }

    def reset_experiment(self) -> None:
        """Reset the experiment by restoring the original chain."""
        self.restore_original()
